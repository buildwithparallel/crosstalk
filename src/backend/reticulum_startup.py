"""Start Reticulum without aborting Crosstalk when one interface fails.

Reticulum calls ``RNS.panic()`` (``os._exit(255)``) if an interface cannot be
created. Crosstalk intercepts that only while synthesizing a named interface,
disables the failed interface in config, and continues with the rest.
"""

from contextlib import contextmanager

import RNS


class ReticulumInterfaceStartupError(RuntimeError):
    """Raised instead of ``RNS.panic()`` while a single interface is starting."""


def disable_interface_in_config(config, interface_name):
    """Turn off a named interface using the same keys Crosstalk's UI uses."""
    if config is None:
        return False

    interfaces = config.get("interfaces") if hasattr(config, "get") else None
    if not interfaces or interface_name not in interfaces:
        return False

    interface = interfaces[interface_name]
    changed = False

    if "enabled" in interface:
        interface["enabled"] = "false"
        changed = True

    if "interface_enabled" in interface:
        interface["interface_enabled"] = "false"
        changed = True

    if "enabled" not in interface and "interface_enabled" not in interface:
        interface["interface_enabled"] = "false"
        changed = True

    return changed


def detach_transport_interfaces_named(interface_name):
    """Drop a half-initialized interface from the live Transport list."""
    transport = getattr(RNS, "Transport", None)
    if transport is None or not hasattr(transport, "interfaces"):
        return

    for interface in list(transport.interfaces):
        if getattr(interface, "name", None) != interface_name:
            continue
        try:
            interface.online = False
        except Exception:
            pass
        try:
            transport.remove_interface(interface)
        except Exception:
            pass


@contextmanager
def recover_failed_interfaces(disabled_names):
    """Patch interface synthesis so a failed interface is disabled, not fatal."""
    original_panic = RNS.panic
    original_synthesize = RNS.Reticulum._synthesize_interface

    def synthesize_and_disable_on_failure(self, config, name, instance_init=False):
        def raise_instead_of_exit():
            raise ReticulumInterfaceStartupError(name)

        RNS.panic = raise_instead_of_exit
        try:
            return original_synthesize(self, config, name, instance_init=instance_init)
        except ReticulumInterfaceStartupError:
            detach_transport_interfaces_named(name)
            if disable_interface_in_config(self.config, name):
                try:
                    self.config.write()
                except Exception as error:
                    RNS.log(
                        f'Crosstalk could not save the disabled interface "{name}": {error}',
                        RNS.LOG_ERROR,
                    )
            disabled_names.append(name)
            message = (
                f'Crosstalk disabled the interface "{name}" because it failed to start. '
                "The rest of the app will continue."
            )
            print(message)
            RNS.log(message, RNS.LOG_ERROR)
            return None
        finally:
            RNS.panic = original_panic

    RNS.Reticulum._synthesize_interface = synthesize_and_disable_on_failure
    try:
        yield
    finally:
        RNS.Reticulum._synthesize_interface = original_synthesize
        RNS.panic = original_panic


def start_reticulum(config_dir):
    """Create a Reticulum instance, disabling interfaces that fail to start."""
    disabled_names = []
    with recover_failed_interfaces(disabled_names):
        reticulum = RNS.Reticulum(config_dir)
    return reticulum, disabled_names
