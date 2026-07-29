# Testing MyLine & looking for bugs

For **#43**: how to test the program and what to do if you find a bug.

## Run

```bash
python myline.py
```

## Basic manual test pass

1. App starts without a traceback.  
2. `myline help c` lists commands.  
3. `myline help paths` shows storage files.  
4. Add/change some data, run `myline check changes`.  
5. `kill` with unsaved changes cancels; `kill f` exits.  
6. Optional: exercise `data`, `net`, `ble` commands you care about.

## If you find a bug

1. Open a **new GitHub issue** on this repo.  
2. Title: short description of the failure.  
3. Body: steps to reproduce, expected vs actual, OS, Python version, traceback.  
4. Fixing it in the same PR is optional — reporting is enough for #43.

## Automated tests (if present)

```bash
python -m unittest discover -s tests -v
```

Only runs if a `tests/` folder exists on the branch.
