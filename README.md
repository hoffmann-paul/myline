# MyLine
MyLine is my own command-line tool.

## Get started
1. Download all files from github.com/hoffmann-paul/myline
2. Install everything in the requirements.txt
3. Run MyLine: `python myline.py`
   - By default it looks for the data file at `Datensätze/data.json`
   - To use a different path, pass `--data-file`, e.g. `python myline.py --data-file path/to/data.json`
For a list of all commands type: `myline help c`

## Commands
If you want to enter more than one word, put it between "Marks".

| Command | Description |
| ----- | ----- |
| `data GET i {parameter} {value}` | Searches for indexes in data.json where `parameter` contains `value` |
| `data HEAD f {index}` | Shows all filled data for an `index` |
| `data HEAD raw {index}` | Shows all data for an `index` |
| `data WRITE t {index} {parameter} {value}` | Overwrites a `Value` for a `Parameter` at an `index` temporary |
| `data WRITE POST {index} {parameter} {value}` | Overwrites a `Value` for a `Parameter` at an `index` and posts it in data.json |
| `data POST a` | Post the data Array in the data.json file |
| `data inspect struc` | Shows a list of all Parameters |
| `data inspect count` | Counts all Data Records |
| `net pg uop {url} {port}` | Tries to connect to a `url` on a specific `port` |
| `ble HEAD devs [raw] [loop]` | Scans BLE Signals and shows a list of Name; Local-Name; rssi; tx_power; MAC-Address; by adding `raw` it also shows devices where name == None, by adding `loop` it rescans every Second |
| `myline help c` | Shows a list of all Commands |
| `myline help info` | Shows Link to GitHub page and MIT License |
| `myline check changes` | Checks if there are some unsaved changes |
| `myline restore changes` | Restore last Sessions Changes |
| `myline kill check` | Checks if there are some unsaved changes; if yes then nothing happens, but if there are no unsaved changes MyLine is killed |
| `myline kill force` | Kills MyLine |

## Command Line Options
| Flag | Description |
| ----- | ----- |
| --data-file {path} | Path to the data.json file to load (defaults to `Datensätze/data.json`) |

## License
This project is licensed under the [MIT License](LICENSE).
