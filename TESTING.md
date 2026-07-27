# Testing MyLine

Quick checklist so contributors can verify the app (issues #43, #76).

## All platforms (macOS / Linux / Windows)

```bash
python myline.py
```

| Check | How | Expected |
| --- | --- | --- |
| Starts | Run above | Banner + prompt, no traceback |
| Help | `myline help c` | Command list |
| Paths | `myline help paths` | Shows configured JSON paths |
| Kill cancel | Change data, `kill` | Warns about unsaved changes, stays open |
| Kill force | `kill f` | Process ends (window may close — #32) |
| Check changes | Delete/rename `data.json`, `myline check changes` | Clear “Can't read …” message (#86) |
| Restore empty | Missing `data_temp.json`, `myline restore changes` | Refuses; data commands still work (#83) |
| WRITE phone | `data WRITE t 0 phone 0491701234567` then inspect | Leading zero kept as string (#84) |
| Tab complete | `da` + Tab (Unix/macOS) | Completes toward `data` (#46) |

## Windows notes (#76)

- Prefer `py -3 myline.py` or `python myline.py` from **cmd.exe** / **PowerShell**.
- Double-click may open a console that `kill` tries to close (#32); IDE terminals (VS Code) should only end the process, not the IDE.
- If something fails only on Windows, open a new issue with: OS build, Python version, exact command, full traceback.

## Automated tests

```bash
python -m unittest discover -s tests -v
```

Covers WRITE coercion (#84) and structural guards (#80, #83, #85, #86).
