import base64
import unittest

import RNS

from src.backend.outbound_identity import (
    DEFAULT_SEND_PATH_TIMEOUT_SECONDS,
    identity_from_public_key_b64,
    parse_path_timeout,
    recall_send_identity,
    remember_destination_identity,
)


class OutboundIdentityTest(unittest.TestCase):
    def test_parse_path_timeout_defaults_to_zero(self):
        self.assertEqual(parse_path_timeout(None), 0)
        self.assertEqual(parse_path_timeout(""), DEFAULT_SEND_PATH_TIMEOUT_SECONDS)
        self.assertEqual(parse_path_timeout("15"), 15.0)
        self.assertEqual(parse_path_timeout(-3), 0)

    def test_restores_identity_from_saved_public_key(self):
        original = RNS.Identity()
        public_key_b64 = base64.b64encode(original.get_public_key()).decode("utf-8")
        restored = identity_from_public_key_b64(public_key_b64)
        self.assertEqual(restored.get_public_key(), original.get_public_key())

    def test_recall_send_identity_uses_announce_key_when_rns_unknown(self):
        original = RNS.Identity()
        destination_hash = bytes(range(16))
        public_key_b64 = base64.b64encode(original.get_public_key()).decode("utf-8")

        recalled = recall_send_identity(destination_hash, public_key_b64)
        self.assertIsNotNone(recalled)
        self.assertEqual(recalled.get_public_key(), original.get_public_key())
        self.assertIsNotNone(RNS.Identity.recall(destination_hash, _no_use=True))

    def test_remember_destination_identity_seeds_recall(self):
        original = RNS.Identity()
        destination_hash = bytes(range(16, 32))
        remember_destination_identity(destination_hash, original)
        recalled = RNS.Identity.recall(destination_hash, _no_use=True)
        self.assertIsNotNone(recalled)
        self.assertEqual(recalled.get_public_key(), original.get_public_key())


if __name__ == "__main__":
    unittest.main()
