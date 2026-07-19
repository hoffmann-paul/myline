# MyLine
MyLine is my own command-line-tool

## Get startet
1. Download all files from github.com/hoffmann-paul/myline
2. Open myline.py in an editor
3. Setup your filepaths for the files
4. Save the file
5. Open myline.py to Start MyLine

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
| myline help | Shows a list of all Commands |
| myline info | Shows Link to GitHub page and MIT Licence |
| myline check changes | Checks if there are some unsaved changes |
| myline kill [force] | Kills the Python Programm, by adding force it dont ask if it should check for unsaved changes |

## Version History
### v1.1.0
*In Progress*
### v1.0.0
The first Version of MyLine with some basic Features.

## License
This project is licensed under the [MIT License](LICENSE).
