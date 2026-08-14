# Interface startup recovery

Reticulum exits the process if a configured interface cannot be created, for
example when a LAN AutoInterface cannot bind UDP port 42671 because another
Reticulum app already owns it.

Crosstalk intercepts that failure for a single interface:

1. The failed interface is turned off in the Reticulum config file.
2. A half-initialized copy is dropped from the live transport list.
3. Remaining interfaces start normally and the app stays up.

The UI shows an alert naming the interfaces that were turned off. You can turn
them back on from **Network Interfaces** after fixing the conflict (stop the
other Reticulum process, or use different AutoInterface ports).

When adding **Local Network (Auto)**, Crosstalk checks for an enabled
AutoInterface that already uses the same group and ports (empty fields mean
Reticulum's defaults: group `reticulum`, discovery `29716`, data `42671`). The
type picker marks that existing interface, the form explains that a second
copy is unnecessary, and Save asks before creating a duplicate.

A broken config file, or two interfaces that share the same name, is still
fatal. Those are not recoverable interface start errors.
