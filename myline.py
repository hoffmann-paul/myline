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
import sys

# --- SETUP VARIABLES ---
file_cmddata_json = 'cmddata.json'
file_company_ids_json = 'company_ids.json'

# --- Configurable data.json path ---
# Precedence: CLI argument > default
DEFAULT_DATA_JSON = 'Datensätze/data.json'

# --- System Variables ---
version = "v1.0.0"

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
    return f"@MyLine {version} [{now.strftime('%H:%M:%S')}]"
 

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

failload = False

Wprint("Loading data.json...")
try:
    with open(file_data_json, 'r') as file:
        data = json.load(file)
        Gprint("Loaded data.json with Success.")
except Exception:
    failload = True
    Rprint("An Error corrupted while trying reading data.json")
    data = []

Wprint("Loading cmddata.json...")
try:
    with open(file_cmddata_json, 'r') as file:
        saves = json.load(file)
        Gprint("Loaded cmddata.json with Success.")
except Exception:
    failload = True
    Rprint("An Error corrupted while trying reading cmddata.json")
    saves = []

Wprint("Loading compandy_id.json...")
try:
    with open(file_company_ids_json, 'r') as file:
        company_ids_raw = json.load(file)
        company_ids = {entry["code"]: entry["name"] for entry in company_ids_raw}
        Gprint("Loaded company_ids.json with Success.")
except Exception:
    failload = True
    Rprint("An Error corrupted while trying reading company_ids.json")
    company_ids = []

Wprint("")
if not failload:
    Gprint("Started MyLine with Success")
else:
    Yprint("Started MyLine with missing Sourcefiles")
Wprint("Type \"myline help c\" for commands")
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

def data_get_i(flags):
    parameter = flags[0]
    value = flags[1]
    found = False
    try:
        for i in data:
            field_value = i.get(parameter, "")
            if isinstance(field_value, str) and value.lower() in field_value.lower():
                found = True
                Gprint("found >>\"" + parameter + "\" contains " + "\"" + str(value) + "\"<< under index " + str(data.index(i)) + " where value is \"" + str(data[data.index(i)][parameter]) + "\"")
        if not found:
            Rprint("nothing found under >>\"" + parameter + "\" contains " + "\"" + str(value) + "\"<<")
    except KeyError:
        Rprint("There is no parameter called >>" + parameter + "<<")

def data_head_f(flags):
    index = flags[0]
    for i in data[int(index)]:
        if str(data[int(index)][i]) != "":
            if data[int(index)][i] != 0:
                m = i + " >>> " + str(data[int(index)][i])
                GGprint(m)

def data_head_raw(flags):
    index = flags[0]
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

def data_post_a(flags):
    try:
        with open(file_data_json, 'w') as file:
            json.dump(data, file)
    except Exception:
        RRprint("Can't POST data as data.json")

def data_write_t(flags):
    index = int(flags[0])
    parameter = flags[1]
    value = flags[2]
    data[index][parameter] = value
    
def data_inspect_struc(flags):
    for i in data[0]:
        Wprint(i)

def data_inspect_count(flags):
    Wprint(f"Counted {len(data)} Objects in data")

def net_pg_uop(flags):
    test_connection(flags[0], int(flags[1]))

def ble_head_devs(flags):
    if flags[0] == "raw":
        show_none = True
    else:
        show_none = False

    if flags[0] == "loop" or flags[1] == "loop":
        stop_event = threading.Event()
        listener = threading.Thread(target=wait_for_stop, args=(stop_event,), daemon=True)
        listener.start()

        while not stop_event.is_set():
            asyncio.run(scan(1.0, show_none))
            Wprint("")
    else:
        asyncio.run(scan(5.0, show_none))

def myline_help_c(flags):
    YYprint("For Explanations visit the Github page:")
    YYprint("github.com/hoffmann-paul/myline/blob/main/README.md")
    YYprint("")
    YYprint("All Commands:")

    for i in commands:
        for j in commands[i]:
            for k in commands[i][j]:
                YYprint(f"{i} {j} {k}")

def myline_help_info(flags):
    Wprint("My Line")
    Wprint("github.com/hoffmann-paul/myline")
    Wprint("")
    Wprint("MIT License")
    Wprint("Copyright (c) 2026 Paul Hoffmann")
    Wprint("Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the \"Software\"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:")
    Wprint("The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.")
    Wprint("THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.")

def myline_check_changes(flags):
    with open(file_data_json, 'r') as file:
        saved_data = json.load(file)
    if saved_data != data:
        Rprint("Unsaved Changes between data and data.json")
    else:
        Gprint("No Unsaved Changes")

def myline_kill_check(flags):
    with open(file_data_json, 'r') as file:
        saved_data = json.load(file)
    if saved_data != data:
        Rprint("Unsaved Changes between data and data.json")
        Rprint("Killing process is canceld...")
    else:
        Gprint("No Unsaved Changes")
        RRprint("Kill MyLine...")
        sys.exit()

def myline_kill_force(flags):
    RRprint("Kill MyLine...")
    sys.exit()

def data_write_post(flags):
    data_write_t(flags)
    data_post_a(flags)

commands = {
    "data": {
        "GET": {
            "i": data_get_i 
        },
        "HEAD": {
            "raw": data_head_raw,
            "f": data_head_f 
        },
        "WRITE": {
            "t": data_write_t,
            "POST": data_write_post
        },
        "POST": {
            "a": data_post_a
        },
        "inspect": {
            "struc": data_inspect_struc,
            "count": data_inspect_count
        }
    },
    "net": {
        "pg": {
            "uop": net_pg_uop 
        }
    },
    "ble": {
        "HEAD": {
            "devs": ble_head_devs
        }
    },
    "myline": {
        "help": {
            "c": myline_help_c,
            "info": myline_help_info
        },
        "check": {
            "changes": myline_check_changes
        },
        "kill": {
            "check": myline_kill_check,
            "force": myline_kill_force
        }
    }
} 

while True:
    now = datetime.datetime.now()
    print(f"\033[34m@MyLine {version} [{now.strftime('%H:%M:%S')}] >>> ", end="")
    raw = input()
    
    # Dispatcher
    try:
        parts = shlex.split(raw)
        if not parts:
            continue
        # Pad incomplete commands so "data" / "data GET" don't IndexError
        while len(parts) < 3:
            parts.append("")
        keyword = parts[0]
        sub_keyword = parts[1]
        sub_sub_keyword = parts[2]
        flags = parts[3:]
        while len(flags) < 5:
                flags.append("")

        if keyword in commands and sub_keyword in commands[keyword] and sub_sub_keyword in commands[keyword][sub_keyword]:
            commands[keyword][sub_keyword][sub_sub_keyword](flags)
        else:
            RRprint(f">>{raw}<< isnt't a vaild command")
    except (ValueError, IndexError, KeyError, TypeError) as e:
            # Normal user input mistakes — don't ask for a GitHub issue 
            RRprint(f"Input error: {e}")
    except Exception as e:
            RRprint(f"Unexpected Error: {e}")
            RRprint("Please open an issue on GitHub")
    Wprint("")
