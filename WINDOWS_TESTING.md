# Windows testing notes

Checklist for **#76** — verify MyLine on Windows. If something fails, open a new issue with OS build, Python version, command, and traceback. You do not have to fix it in the same PR.

## Run

```bat
py -3 myline.py
```

or:

```bat
python myline.py
```

From **cmd.exe** or **PowerShell**. Double-click also works but uses its own console window.

## Smoke checks

| Step | Command / action | OK if |
| --- | --- | --- |
| Start | run above | Banner + prompt, no crash |
| Help | `myline help c` | Lists commands |
| Paths | `myline help paths` | Shows JSON paths |
| Kill cancel | edit data, then `kill` | Warns unsaved, stays open |
| Kill force | `kill f` | Process ends |
| Check files | `myline check files` | Reports load status |

## Known differences vs Unix

- Tab completion needs a readline backend; Windows may need `pyreadline3` if Tab does nothing.
- Closing the console window on `kill` is best-effort (see #32).
- Paths use backslashes in display sometimes; configured paths still work.

## Report a bug

Open an issue titled like `Windows: <what broke>` and paste:

1. Windows version  
2. `py -3 --version`  
3. Exact steps  
4. Full error text  
