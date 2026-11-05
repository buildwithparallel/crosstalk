"""Start Reticulum without aborting Crosstalk when one interface fails.

Reticulum calls ``RNS.panic()`` (``os._exit(255)``) if an interface cannot be
created. Crosstalk intercepts that only while synthesizing a named interface,
disables the failed interface in config, and continues with the rest.
"""

from contextlib import contextmanager
from functools import wraps

import RNS

from src.backend.rnode_ble import install_rnode_ble_dependency_guard


class ReticulumInterfaceStartupError(RuntimeError):
    """Raised instead of ``RNS.panic()`` while a single interface is starting."""


def defer_initial_radio_connection(interface_class):
    """Use RNode's reconnect worker instead of waiting for a radio at startup."""
    original_init = interface_class.__init__
    original_open = interface_class.open_port
    if getattr(original_init, "_crosstalk_background_connection", False):
        return False

    @wraps(original_init)
    def initialize(self, *args, **kwargs):
        self._crosstalk_initializing_radio = True
        try:
            return original_init(self, *args, **kwargs)
        finally:
            self._crosstalk_initializing_radio = False

    @wraps(original_open)
    def open_port(self, *args, **kwargs):
        if getattr(self, "_crosstalk_initializing_radio", False):
            # All radio state is initialized before this call. Upstream catches
            # this connection error and starts its normal reconnect worker,
            # which keeps the same interface and saved settings alive.
            raise ConnectionError("Radio connection pending; connecting in the background")
        return original_open(self, *args, **kwargs)

    initialize._crosstalk_background_connection = True
    interface_class.__init__ = initialize
    interface_class.open_port = open_port
    return True


def install_background_radio_connections():
    from RNS.Interfaces.RNodeInterface import RNodeInterface
    from RNS.Interfaces.RNodeMultiInterface import RNodeMultiInterface

    for interface_class in (RNodeInterface, RNodeMultiInterface):
        defer_initial_radio_connection(interface_class)


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
        # Device disconnects and reboots are normal in a desktop app. Reticulum
        # loads this setting before synthesis, so override even a legacy config
        # that requested a process-wide abort on a runtime interface error.
        RNS.Reticulum.panic_on_interface_error = False

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
    install_rnode_ble_dependency_guard()
    install_background_radio_connections()
    disabled_names = []
    with recover_failed_interfaces(disabled_names):
        reticulum = RNS.Reticulum(config_dir)
    return reticulum, disabled_names
