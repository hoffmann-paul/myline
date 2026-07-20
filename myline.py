import json
import shlex
import socket
import threading
import asyncio
from bleak import BleakScanner
import datetime
import subprocess
import argparse
import platform

# SETUP VARIABLES
file_cmddata_json = 'cmddata.json'
file_company_ids_json = 'company_ids.json'

# --- Configurable data.json path ---
# Precedence: CLI argument > default
DEFAULT_DATA_JSON = 'Datensätze/data.json'

parser = argparse.ArgumentParser(description="MyLine")
parser.add_argument(
    "--data-file",
    dest="data_file",
    default=DEFAULT_DATA_JSON,
    help="Path to the data.json file (defaults to '%(default)s')"
)
args = parser.parse_args()

file_data_json = args.data_file

def _prefix():
    now = datetime.datetime.now()
    return f"@MyLine v1.0.0 [{now.strftime('%H:%M:%S')}]"
 

def Gprint(string):
    print(f"\033[32m{_prefix()} {string}\033[0m")
 
def GGprint(string):
    print(f"\033[0;42m{_prefix()} {string}\033[0m")

def Rprint(string):
    print(f"\033[31m{_prefix()} {string}\033[0m")
 
def RRprint(string):
    print(f"\033[0;41m{_prefix()} {string}\033[0m")

def Yprint(string):
    print(f"\033[33m{_prefix()} {string}\033[0m")
 
def YYprint(string):
    print(f"\033[0;43m{_prefix()} {string}\033[0m")

def Bprint(string):
    print(f"\033[34m{_prefix()} {string}\033[0m")
 
def BBprint(string):
    print(f"\033[0;44m{_prefix()} {string}\033[0m")

def Wprint(string):
    print(f"\033[0m{_prefix()} {string}\033[0m")
 
def WWprint(string):
    print(f"\033[0;47;30m{_prefix()} {string}\033[0m")

Wprint("-" * 60)
Wprint("Started MyLine...")
Wprint("")
Wprint(f"Using data file: {file_data_json}")
Wprint("")

try:
    with open(file_data_json, 'r') as file:
        data = json.load(file)
    with open(file_cmddata_json, 'r') as file:
        saves = json.load(file)
    with open(file_company_ids_json, 'r') as file:
        company_ids_raw = json.load(file)

    company_ids = {entry["code"]: entry["name"] for entry in company_ids_raw}
    Gprint("All Source Files loaded")
except Exception:
    Rprint("An Error corrupted while trying reading source files")

Wprint("")
Gprint("Started MyLine with Success")
Wprint("Type \"myline help\" for commands")
Wprint("")
now = datetime.datetime.now()
Wprint(f"Now is: {now}")
Wprint("")

known_devices = {}
for entry in saves:
    for name, info in entry.get("BLE-Adresse", {}).items():
        addr = info.get("adress", "")

        if isinstance(addr, str):
            addr_list = [addr] if addr else []
        elif isinstance(addr, list):
            addr_list = addr
        else:
            addr_list = []

        for a in addr_list:
            if a:
                known_devices[a.lower()] = name

def resolve_manufacturer(manufacturer_data):
    for company_id in manufacturer_data:
        if company_id in company_ids:
            return company_ids[company_id]
    return None

def test_connection(host="8.8.8.8", port=53, timeout=3):
            try:
                socket.setdefaulttimeout(timeout)
                socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
                Gprint(f"Success for pinging {host} on {port}")
            except Exception as e:
                Rprint(f"can't reach {host} error: {e}")

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        s.close()
        
    if local_ip == "127.0.0.1":
        return False
    
    return local_ip

async def scan(time, show_none=False):
    devices = await BleakScanner.discover(timeout=time, return_adv=True)
    for address, (device, adv_data) in devices.items():
        try:
            name = device.name
        except Exception:
            name = None

        if name is not None or show_none:
            now = datetime.datetime.now()
            line = f"[{now.time()}]  {name}   {adv_data.local_name}   {adv_data.rssi}   {adv_data.tx_power}   {address}"

            manufacturer = resolve_manufacturer(adv_data.manufacturer_data)
            if manufacturer:
                line += f"   ({manufacturer})"

            known_name = known_devices.get(address.lower())
            if known_name:
                Yprint(f"{line}   <<<  {known_name}")
            else:
                Wprint(line)

def wait_for_stop(stop_event):
    input() 
    stop_event.set()

def launch_app(application):
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.run(["open", "-a", application], check=True)
        elif system == "Windows":
            # 'start' is a cmd.exe builtin, not a standalone executable,
            # so it has to go through the shell. The empty "" is the
            # window-title argument that 'start' expects before the target.
            subprocess.run(f'start "" "{application}"', shell=True, check=True)
        elif system == "Linux":
            # run the # executable directly (it needs to be in PATH).
            subprocess.run([application], check=True)
        else:
            Rprint(f"Unsupported operating system: {system}")
            return
        Gprint(f"Launched >>{application}<<")
    except Exception as e:
        RRprint(f"Couldn't launch >>{application}<< on {system}: {e}")

while True:
    now = datetime.datetime.now()
    print(f"\033[34m@MyLine v1.0.0 [{now.strftime('%H:%M:%S')}] >>> ", end="")
    raw = input()

    cmd = []
    cmd = shlex.split(raw)
    
    cmd += [""] * 12

    try:
        if cmd[0] == "data":
            if cmd[1] == "GET":
                if cmd[2] == "i":
                    parameter = cmd[3]
                    if cmd[4] == "c":
                        value = cmd[5]
                        found = False
                        try:
                            for i in data:
                                field_value = i.get(parameter, "")
                                if isinstance(field_value, str) and value.lower() in field_value.lower():
                                    found = True
                                    Gprint("found >>\"" + parameter + "\" contains " + "\"" + str(value) + "\"<< under index " + str(data.index(i)) + " where value is \"" + str(data[data.index(i)][parameter]) + "\"")
                            if not found:
                                Rprint("nothing found under >>\"" + parameter + "\" contains " + "\"" + str(value) + "\"")
                        except KeyError:
                            Rprint("There is no parameter called >>" + parameter + "<<")
                    else:
                        value = cmd[4]
                        found = False
                        try:
                            for i in data:
                                if i[parameter] == value:
                                    found = True
                                    Gprint("found >>\"" + parameter + "\" == " + "\"" + str(value) + "\"<< under index " + str(data.index(i)))
                                else:
                                    # Only try integer comparison if the field value is an integer
                                    field_value = i[parameter]
                                    if isinstance(field_value, int):
                                        try:
                                            int_value = int(value)
                                            if field_value == int_value:
                                                found = True
                                                Gprint("found >>\"" + parameter + "\" == " + "\"" + str(value) + "\"<< under index " + str(data.index(i)))
                                            else:
                                                if not found:
                                                    found = False
                                        except ValueError:
                                            Rprint(f"Value '{value}' cannot be compared as integer for parameter '{parameter}'")
                                            break
                        except KeyError:
                            Rprint("There is no parameter called >>" + parameter +"<<")
                        else:
                            if not found:
                                Rprint("nothing found under >>\"" + parameter + "\" == " + "\"" + str(value) + "\"")
                else:
                    RRprint(f">>{raw}<< isnt't a vaild command")
            elif cmd[1] == "HEAD":
                index = int(cmd[2])
                flags = cmd[3:]
                try:
                    if "raw" in flags:
                        for i in data[int(index)]:
                            if str(data[int(index)][i]) != "":
                                if data[int(index)][i] != 0:
                                    if data[int(index)][i] != {}:
                                        if data[int(index)][i] != []:
                                            m = i + " >>> " + str(data[int(index)][i]) 
                                            GGprint(m)
                                        else:
                                            m = i + " >>> " + str(data[int(index)][i]) 
                                            RRprint(m)
                                    else:
                                        m = i + " >>> " + str(data[int(index)][i]) 
                                        RRprint(m)
                                else:
                                    m = i + " >>> " + str(data[int(index)][i]) 
                                    RRprint(m)
                            else:
                                m = i + " >>> " + str(data[int(index)][i]) 
                                RRprint(m)

                    else:
                        for i in data[int(index)]:
                            if str(data[int(index)][i]) != "":
                                if data[int(index)][i] != 0:
                                    m = i + " >>> " + str(data[int(index)][i])
                                    GGprint(m)
                except ValueError:
                    RRprint("Index muss be and Integer")
                except IndexError:
                    RRprint("This Index is out of Range")
            elif cmd[1] == "WRITE":
                index = int(cmd[2])
                parameter = cmd[3]
                value = cmd[4]
                data[index][parameter] = value
            elif cmd[1] == "POST":
                try:
                    with open(file_data_json, 'w') as file:
                        json.dump(data, file)
                except Exception:
                    RRprint("Can't POST data as data.json")
            elif cmd[1] == "inspect":
                if cmd[2] == "struc":
                    for i in data[0]:
                        Wprint(i)
                elif cmd[2] == "count":
                    Wprint(f"Counted {len(data)} Objects in data")
                else:
                    RRprint(f">>{raw}<< isnt't a vaild command")
            else:
                RRprint(f">>{raw}<< isnt't a vaild command")
        elif cmd[0] == "net":
            if cmd[1] == "pg":
                url = cmd[2]
                port = int(cmd[3])

                test_connection(url, port)
            elif cmd[1] == "GET":
                if cmd[2] == "ip":
                    ip = get_local_ip()
                    if ip != False:
                        Gprint(ip)
                    else:
                        Rprint("No active connection found")
                else:
                    RRprint(f">>{raw}<< isnt't a vaild command")
            else:
                RRprint(f">>{raw}<< isnt't a vaild command")
        elif cmd[0] == "ble":
            if cmd[1] == "HEAD":
                if cmd[2] == "devs":
                    if cmd[3] == "raw":
                        show_none = True
                    else:
                        show_none = False
                    
                    if cmd[3] == "loop" or cmd[4] == "loop":
                        stop_event = threading.Event()
                        listener = threading.Thread(target=wait_for_stop, args=(stop_event,), daemon=True)
                        listener.start()

                        while not stop_event.is_set():
                            asyncio.run(scan(1.0, show_none))
                            Wprint("")
                    else:
                        asyncio.run(scan(5.0, show_none))
                else:
                    RRprint(f">>{raw}<< isnt't a vaild command")
            else:
                RRprint(f">>{raw}<< isnt't a vaild command")
        elif cmd[0] == "app":
            if cmd[1] == "lch":
                try:
                    application = saves[0]["Applications"][cmd[2]]
                except (KeyError, IndexError):
                    RRprint(f"MyLine doesn't support an Application named >>{cmd[2]}<<")
                else:
                    launch_app(application)
            elif cmd[1] == "list":
                for i in saves[0]["Applications"]:
                    Wprint(saves[0]["Applications"][i])
            else:
                RRprint(f">>{raw}<< isnt't a vaild command")
        elif cmd[0] == "myline":
            if cmd[1] == "help":
                YYprint("For Explanations visit the Github page:")
                YYprint("github.com/hoffmann-paul/myline/blob/main/README.md")
                YYprint("")
                YYprint("All Commands:")
                YYprint("data GET i {parameter} {value}")
                YYprint("data GET i {parameter} c {value}")
                YYprint("data HEAD {i} [raw]")
                YYprint("data WRITE {i} \"{parameter}\" \"{value}\"")
                YYprint("data POST")
                YYprint("data inspect struc")
                YYprint("data inspect count")
                YYprint("net pg {url} {port}")
                YYprint("ble HEAD devs [raw] [loop]")
                YYprint("app lch {App}")
                YYprint("app list")
                YYprint("myline help")
                YYprint("myline info")
                YYprint("myline check changes")
                YYprint("myline kill [force]")
            elif cmd[1] == "info":
                Wprint("My Line")
                Wprint("github.com/hoffmann-paul/myline")
                Wprint("")
                Wprint("MIT License")
                Wprint("Copyright (c) 2026 Paul Hoffmann")
                Wprint("Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:")
                Wprint("The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.")
                Wprint("THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.")
            elif cmd[1] == "check":
                if cmd[2] == "changes":
                    with open(file_data_json, 'r') as file:
                        saved_data = json.load(file)
                    if saved_data != data:
                        Rprint("Unsaved Changes between data and data.json")
                    else:
                        Gprint("No Unsaved Changes")
                else:
                    RRprint(f">>{raw}<< isnt't a vaild command")
            elif cmd[1] == "kill":
                if cmd[2] != "force":
                    Wprint("Check for unsaved change before killing MyLine")
                    Bprint("[Y/N]")
                    answer = input()
                    if answer == "Y" or answer == "y":
                        with open(file_data_json, 'r') as file:
                            saved_data = json.load(file)
                        if saved_data != data:
                            Rprint("Unsaved Changes between data and data.json")
                            Rprint("Killing process is canceld...")
                        else:
                            Gprint("No Unsaved Changes")
                            RRprint("Kill MyLine...")
                            quit()
                    elif answer == "N" or answer == "n":
                        RRprint("Kill MyLine...")
                        quit()
                    else:
                        RRprint(f">>{answer}<< isnt's a valid input")
                elif cmd[2] == "force":
                    RRprint("Kill MyLine...")
                    quit()
                else:
                    RRprint(f">>{raw}<< isnt't a vaild command")
            else:
                RRprint(f">>{raw}<< isnt't a vaild command")
        else:
            RRprint(f">>{raw}<< isnt't a vaild command")
    except Exception:
        RRprint("Something went wrong")

    Wprint("")
