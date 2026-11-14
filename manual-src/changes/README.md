# Changes since the last release, one file per feature

Each feature branch writes its notes in its own file here, for example `locations.md`, instead of adding to the list
at the bottom of "Changes since the last release" in ../WORKFLOW.md. Separate files mean two PRs never edit the same
lines, so merging one does not put the others in conflict.

What to write: what was built, the choice Callum made (demo option, date), the S keys and functions involved, the
test that covers it, and anything not yet checked by Callum. At the next package, fold these notes (and the older ones
in WORKFLOW.md) into HISTORY in make_manual.py, then delete the files.
