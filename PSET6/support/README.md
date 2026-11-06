# Pset 6 programming code — Fall 2026

This folder contains the starter code for the sponsored-search-auctions programming assignment.

## Requirements

- Python 3.10 or newer is recommended.
- The assignment uses only the Python standard library.
- `pandas` and `numpy` are **not** required.

Use `python3` in the commands below. On a system where `python` already means Python 3, either command is fine.

## Create your team files

From this folder, run:

```bash
python3 start.py TEAMNAME
```

For a team named `abxy`, this creates:

```text
abxybb.py       (class Abxybb)
abxybudget.py   (class Abxybudget)
```

The script automatically gives each file the class name expected by the simulator. It refuses to overwrite an existing file. Use `--force` only when you intentionally want to replace prior work:

```bash
python3 start.py TEAMNAME --force
```

## Tests

The supplied GSP and simulator tests should pass immediately:

```bash
python3 test_gsp.py
python3 test_simulator.py
```

After implementing the balanced-bidding TODOs, run:

```bash
python3 test_bb.py TEAMNAME
```

If exactly one generated `*bb.py` file is present, `python3 test_bb.py` also works without the team name.

After implementing the VCG payment TODO, run:

```bash
python3 test_vcg.py
```

The test files are also compatible with `pytest`, but `pytest` is optional and is not needed for this assignment.

## Run the simulator

Examples:

```bash
python3 auction.py --help
python3 auction.py --num-rounds 2 --perms 1 --seed 1 Truthful,5
python3 auction.py --perms 1 --iters 2 --reserve 40 --seed 1 Truthful,5
```

Agent names on the command line are matched case-insensitively. Both of these therefore work after generating the `abxy` team files:

```bash
python3 auction.py --perms 10 --iters 200 Truthful,4 Abxybb,1
python3 auction.py --perms 10 --iters 200 Truthful,4 abxybb,1
```

Ordinary runs print only summaries. To see every round while debugging, add:

```bash
--loglevel debug
```

## Units and budgets

Values, bids, reserve prices, and budgets are measured in integer **cents**. For example, the competition budget of $600 is passed as:

```bash
--budget 60000
```

`history.agents_spent[i]` gives agent `i`'s cumulative spending through the most recently completed round.

## Files students should edit

- `TEAMNAMEbb.py`
- `TEAMNAMEbudget.py`
- `vcg.py`

Do not modify the simulator files for your submission unless the assignment instructions explicitly tell you to do so.
