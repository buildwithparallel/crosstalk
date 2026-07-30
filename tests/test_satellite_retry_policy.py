import time
import unittest

import LXMF

from src.backend.satellite_retry_policy import SatelliteRetryPolicy


class FakeMessage:
    def __init__(self):
        self.state = LXMF.LXMessage.OUTBOUND
        self.delivery_attempts = 1
        self.actual_sends = 0
        self.send = self._send

    def _send(self):
        self.actual_sends += 1
        self.state = LXMF.LXMessage.SENT

    def __str__(self):
        return "FakeMessage"


class FakeRouter:
    def __init__(self, message):
        self.pending_outbound = [message]
        self.failed_messages = []

    def fail_message(self, message):
        if message in self.pending_outbound:
            self.pending_outbound.remove(message)
        message.state = LXMF.LXMessage.FAILED
        self.failed_messages.append(message)


class SatelliteRetryPolicyTest(unittest.TestCase):
    def wait_until(self, callback, timeout=0.5):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if callback():
                return True
            time.sleep(0.005)
        return callback()

    def make_policy(self, max_attempts):
        return SatelliteRetryPolicy(
            retry_delay_seconds=0.03,
            max_attempts=max_attempts,
            minimum_retry_delay_seconds=0,
            poll_interval_seconds=0.002,
        )

    def test_defaults_to_one_attempt_for_enabled_iridium(self):
        policy = SatelliteRetryPolicy.from_reticulum_config({
            "interfaces": {
                "Satellite": {
                    "type": "IridiumIMTInterface",
                    "interface_enabled": "yes",
                },
            },
        })

        self.assertEqual(policy.retry_delay_seconds, 600)
        self.assertEqual(policy.max_attempts, 1)

    def test_does_not_change_non_satellite_instances(self):
        policy = SatelliteRetryPolicy.from_reticulum_config({
            "interfaces": {
                "Internet": {
                    "type": "TCPClientInterface",
                    "interface_enabled": "yes",
                },
                "Disabled Satellite": {
                    "type": "IridiumIMTInterface",
                    "interface_enabled": "no",
                },
            },
        })

        self.assertIsNone(policy)

    def test_one_attempt_fails_only_after_full_proof_window(self):
        message = FakeMessage()
        router = FakeRouter(message)
        policy = self.make_policy(max_attempts=1)
        policy.guard_message(message, router)

        message.send()

        self.assertEqual(message.actual_sends, 1)
        self.assertNotIn(message, router.pending_outbound)
        self.assertEqual(router.failed_messages, [])
        self.assertTrue(self.wait_until(lambda: message.state == LXMF.LXMessage.FAILED))
        self.assertEqual(message.actual_sends, 1)

    def test_two_attempts_are_separated_and_capped(self):
        message = FakeMessage()
        router = FakeRouter(message)
        policy = self.make_policy(max_attempts=2)
        policy.guard_message(message, router)

        message.send()

        self.assertEqual(message.actual_sends, 1)
        self.assertTrue(self.wait_until(lambda: message.actual_sends == 2))
        self.assertTrue(self.wait_until(lambda: message.state == LXMF.LXMessage.FAILED))
        self.assertEqual(message.actual_sends, 2)

    def test_proof_stops_retry_immediately(self):
        message = FakeMessage()
        router = FakeRouter(message)
        policy = self.make_policy(max_attempts=2)
        policy.guard_message(message, router)

        message.send()
        message.state = LXMF.LXMessage.DELIVERED

        time.sleep(0.08)
        self.assertEqual(message.actual_sends, 1)
        self.assertEqual(router.failed_messages, [])
        self.assertEqual(message.state, LXMF.LXMessage.DELIVERED)


if __name__ == "__main__":
    unittest.main()
