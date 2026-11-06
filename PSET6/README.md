# PSET6 - Cameron and Justin

Team identifier: `cwjc`

## Files to upload to Canvas

- `cwjcbb.py`
- `cwjcbudget.py`
- `vcg.py`
- `cwjcsolution.tex`
- `cwjcsolution.pdf`

`support/` contains the supplied simulator and test scripts. It does not duplicate the three submitted Python files; local commands add the parent directory to Python's module path so the simulator and tests use those submitted files.

## Run locally

From this directory, run the supplied checks with:

```sh
cd support
PYTHONPATH=.. python3 test_gsp.py
PYTHONPATH=.. python3 test_simulator.py
PYTHONPATH=.. python3 test_bb.py cwjc
PYTHONPATH=.. python3 test_vcg.py
```

Example experiment:

```sh
cd support
PYTHONPATH=.. python3 auction.py --perms 1 --seed 2 --iters 200 cwjcbb,5
```

The LaTeX source and PDF contain the written answers and experiment results.
