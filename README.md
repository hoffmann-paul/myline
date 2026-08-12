# MyLine
MyLine is my own command-line tool. There are one main Feature. The editing and storing of Data Record. Also some Network and Bluetooth commands are excisting. Feel free zu add any sort of Command.

## Get started

Windows users: see **[WINDOWS_TESTING.md](WINDOWS_TESTING.md)** for a short smoke checklist (#76).
Contributors: **[TESTING.md](TESTING.md)** — how to test and report bugs (#43).

1. Download all files from **[The GitHub Page](github.com/hoffmann-paul/myline)**
   myline/
   ├── .github/
   │   └── ISSUE_TEMPLATE/
   │       ├── bug_report.md
   │       ├── bug-report-by-ai.md
   │       └── feature_request.md
   ├── .gitignore
   ├── LICENSE
   ├── myline.py
   ├── README.md
   ├── requirements.txt
   ├── storage/
   │   ├── cmddata.json
   │   ├── cmdhistory.json
   │   ├── company_ids.json
   │   ├── data_temp.json
   │   └── data.json
   ├── TESTING.md
   ├── tests/
   │   ├── test_coerce_write_value.py
   │   └── test_completion.py
   └── WINDOWS_TESTING.md
2. Install everything in the requirements.txt
3. Run MyLine: `python myline.py`
   - By default storage files live under `storage/` (`data.json`, `cmddata.json`, `company_ids.json`, `cmdhistory.json`, `data_temp.json`)
   - Override any path with CLI flags, e.g. `python myline.py --data-file path/to/data.json --cmdhistory-file /tmp/hist.json`
   - Press <kbd>Tab</kbd> to autocomplete the current command part (top-level, sub-keyword, or sub-sub-keyword). Disable with `python myline.py --no-completion` for piping input.
For a list of all commands, type: `myline help c`

## How to operate
- There are Two ways to operate MyLine:
   - `Commands`: You need Commands to do Things in MyLine they are build out of Three `Command Parts`, `Flags` and `Keys`.
   - `Shortcuts`: Shortcuts are one Word commands and can't have `Flags`.

### Commands
- `Flags` you need to replace it with your own value.  
- `Keys` can you add or not, it is doesn't matter in which sequence you add them.  
- If you want to enter more than one word, put it between "Marks".
- You need to seperate every part of the Command with a whitespace.  

| Command | Flags | Keys | Description |
| ----- | ----- | ----- | ----- |
| `data GET i` | `parameter` `value`|  | Searches for indexes in data.json where `parameter` contains `value` |
| `data GET im` | `search amount` |  | Works excactly like `data GET i` but you can search with multiple conditions |
| `data HEAD f` | `index` |  | Shows all filled data for an `index` |
| `data HEAD raw` | `index` |  | Shows all data for an `index` |
| `data WRITE t` | `index` `parameter` `value` |  | Overwrites a `Value` for a `Parameter` at an `index` temporarily |
| `data WRITE POST` | `index` `parameter` `value` |  | Overwrites a `Value` for a `Parameter` at an `index` and posts it in data.json |
| `data POST a` |  |  | Post the data Array in the data.json file |
| `data card new` |  |  | Creates a new Data Record shows the matching index and ask for a value for every parameter |
| `data card delete` | `index` |  | Deletes a Data Record permanently |
| `data inspect struc` |  |  | Shows a list of all Parameters |
| `data inspect count` |  |  | Counts all Data Records |
| `net pg uop` | `url` `port` |  | Tries to connect to a `url` on a specific `port` |
| `ble HEAD devs` |  | `raw` `loop` | Scans BLE Signals and shows a list of Name; Local-Name; rssi; tx_power; MAC-Address; by adding `raw` it also shows devices where name == None, by adding `loop` it rescans every Second |
| `myline help c` |  |  | Shows a list of all Commands |
| `myline help info` |  |  | Shows Link to GitHub page and MIT License |
| `myline help paths` |  |  | Shows all file paths |
| `myline history GET` |  |  | Shows the full Command History |
| `myline history clear` |  |  | Clears the Command History |
| `myline check changes` |  |  | Checks if there are some unsaved changes |
| `myline check files` |  |  | Checks if all Sourcefiles loaded at the Programm start |
| `myline check backup` |  |  | List all Backup files |
| `myline restore changes` |  |  | Restore last Sessions Changes |
| `myline config HEAD` |  |  | Shows a list of all configurable settings and there current state |
| `myline config switch` | `configuration` | `true` `false` | changes a `configuration` to `true` or `false` |
| `myline backup save` |  |  | Saves the `storage` folder in a .zip file in `backups` |
| `myline backup restore` |  |  | Replaces the `storage` folder with the last backup |

### Shortcuts
- `Keys` can you add or not, it is doesn't matter in which sequence you add them.

| Shortcut | Keys | Description |
| ----- | ----- | ----- |
| `kill` | | Checks if there are some unsaved changes; if yes then nothing happens, but if there are no unsaved changes MyLine is killed |
| `kill f` | | Kills MyLine |
| `last` | | Repeats the last Commnd if possible, you can only repeat commands without `flags` and `keys` |

## Command Line Options
| Flag | Description |
| ----- | ----- |
| --data-file {path} | Path to data.json (default `storage/data.json`) |
| --cmddata-file {path} | Path to cmddata.json (default `storage/cmddata.json`) |
| --company-ids-file {path} | Path to company_ids.json (default `storage/company_ids.json`) |
| --cmdhistory-file {path} | Path to cmdhistory.json (default `storage/cmdhistory.json`) |
| --data-temp-file {path} | Path to data_temp.json auto-save (default `storage/data_temp.json`) |
| --no-completion | Disable interactive Tab completion (useful for piped / scripted input) |

## License
This project is licensed under the [MIT License](LICENSE).
