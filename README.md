# MyLine
MyLine is my own command-line-tool
## Get startet
1. Download all files from github.com/hoffmann-paul/myline
2. Install everything in the requirements.txt
3. Run MyLine: `python myline.py`
   - By default it looks for the data file at `Datensätze/data.json`
   - To use a different path, pass `--data-file`, e.g. `python myline.py --data-file path/to/data.json`
For a list of all commands type: `myline help`
## Commands
If you wanna enter more than one word pur it between "Marks"
| Command | Description |
| ----- | ----- |
| data GET i {parameter} {value} | Shows and index of a Data Record by entering a parameter and a value |
| data HEAD {i} [raw] | Shows all filled data for an index (i), by adding raw it also shows data that is "" or 0 |
| data WRITE {i} {parameter} {value} | Overwrites a Value for a Parameter at an index temporary |
| data POST | Saves tha data Array in the data.json file |
| data inspect struc | Shows all Parameters |
| data inspect count | Counts all Data Records |
| net pg {url} {port} | Trys pinging a URL on a specific Port |
| ble HEAD devs [raw] [loop] | Scans BLE Signals and shows an list of Name; Local-Name; rssi; tx_power; MAX-Adress; by adding raw it also shows devices where name == None, by adding loop it rescans every Second |
| app lch {App} | Launches an application configured in cmddata.json |
| app list | Shows a List of every application configured in cmddata.json |
| myline help | Shows a list of all Commands |
| myline info | Shows Link to GitHub page and MIT Licence |
| myline debug | Toggle the debug mode, if Debug mode is enabled it shows an error message when crashing instead of "Something went wrong" |
| myline check changes | Checks if there are some unsaved changes |
| myline kill [force] | Kills the Python Programm, by adding force it dont ask if it should check for unsaved changes |
## Command Line Options
| Flag | Description |
| ----- | ----- |
| --data-file {path} | Path to the data.json file to load (defaults to `Datensätze/data.json`) |
## License
This project is licensed under the [MIT License](LICENSE).
