# Fall 2026 release changes

The student TODOs in the balanced-bidding agent and VCG mechanism remain intentionally incomplete. The release infrastructure was updated as follows:

- Removed IDE metadata, compiled bytecode, and macOS archive metadata.
- Removed unconditional console prints from `history.py`.
- Moved per-round and per-iteration traces to `--loglevel debug`.
- Fixed `history.agents_spent` so agents see spending through the previous completed round.
- Fixed the GSP-to-VCG switch for an odd number of rounds.
- Made agent class loading case-insensitive and improved error messages.
- Updated `start.py` to create correctly named team classes automatically.
- Made `start.py` refuse to overwrite work unless `--force` is supplied.
- Made all test files runnable directly as scripts while retaining pytest compatibility.
- Made `test_bb.py` locate the generated team agent rather than importing a nonexistent `bbagent.py`.
- Replaced permissive truncation-based balanced-bidding assertions with exact integer-cent checks.
- Added simulator regression tests for budget history and mechanism switching.
- Made the template's initial bid an integer number of cents.
- Standardized commands and shebangs on Python 3.
- Clarified that the project has no third-party runtime dependencies.
