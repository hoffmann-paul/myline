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

# Tab completion is provided by the stdlib ``readline`` module on Unix
# and macOS. On Windows ``readline`` is not bundled with CPython by default,
# so we degrade gracefully — typing still works, Tab just falls through.
try:
    import readline  # noqa: F401  (presence is enough; functions used below)
    _READLINE_AVAILABLE = True
except ImportError:  # pragma: no cover - exercised on Windows without pyreadline
    readline = None  # type: ignore[assignment]
    _READLINE_AVAILABLE = False

# --- SETUP VARIABLES (defaults; overridable via CLI) ---
# Precedence for each path: CLI argument > default under storage/
DEFAULT_DATA_JSON = 'storage/data.json'
DEFAULT_CMDDATA_JSON = 'storage/cmddata.json'
DEFAULT_COMPANY_IDS_JSON = 'storage/company_ids.json'
DEFAULT_CMDHISTORY_JSON = 'storage/cmdhistory.json'
DEFAULT_DATA_TEMP_JSON = 'storage/data_temp.json'

# --- System Variables ---
version = "v1.0.0"
data = []
history = []
loaded_cmddata_json = False
loaded_cmdhistory_json = False
loaded_company_ids_json = False
loaded_data_temp_json = False
loaded_data_json = False

parser = argparse.ArgumentParser(description="MyLine")
parser.add_argument(
    "--no-completion",
    dest="no_completion",
    action="store_true",
    help="Disable interactive Tab completion (useful for piping input).",
)
parser.add_argument(
    "--data-file",
    dest="data_file",
    default=DEFAULT_DATA_JSON,
    help="Path to the data.json file (defaults to '%(default)s')",
)
parser.add_argument(
    "--cmddata-file",
    dest="cmddata_file",
    default=DEFAULT_CMDDATA_JSON,
    help="Path to the cmddata.json file (defaults to '%(default)s')",
)
parser.add_argument(
    "--company-ids-file",
    dest="company_ids_file",
    default=DEFAULT_COMPANY_IDS_JSON,
    help="Path to the company_ids.json file (defaults to '%(default)s')",
)
parser.add_argument(
    "--cmdhistory-file",
    dest="cmdhistory_file",
    default=DEFAULT_CMDHISTORY_JSON,
    help="Path to the cmdhistory.json file (defaults to '%(default)s')",
)
parser.add_argument(
    "--data-temp-file",
    dest="data_temp_file",
    default=DEFAULT_DATA_TEMP_JSON,
    help="Path to the data_temp.json auto-save file (defaults to '%(default)s')",
)
args = parser.parse_args()

file_data_json = args.data_file
file_cmddata_json = args.cmddata_file
file_company_ids_json = args.company_ids_file
file_cmdhistory_json = args.cmdhistory_file
file_data_temp_json = args.data_temp_file

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

failload = False

Wprint("Loading Source files")

try:
    with open(file_data_json, 'r') as file:
        data = json.load(file)
        loaded_data_json = True
except Exception:
    failload = True
    data = []

try:
    with open(file_cmdhistory_json, 'r') as file:
        history = json.load(file)
        loaded_cmdhistory_json = True
except Exception:
    failload = True
    history = []

try:
    with open(file_cmddata_json, 'r') as file:
        saves = json.load(file)
        loaded_cmddata_json = True
except Exception:
    failload = True
    saves = []

try:
    with open(file_company_ids_json, 'r') as file:
        company_ids_raw = json.load(file)
        company_ids = {entry["code"]: entry["name"] for entry in company_ids_raw}
        loaded_company_ids_json = True
except Exception as e:
    failload = True
    company_ids = {}

try:
    with open(file_data_temp_json, 'r') as file:
        temp_data = json.load(file)
        loaded_data_temp_json = True
except Exception:
    failload = True
    temp_data = 0

def check_temp_saves():
    if temp_data != 0:
        if temp_data == []:
            return False
        else:
            return True
    else:
        Rprint("data_temp.json is missing")
        return False

Wprint("")
if not failload:
    Gprint("Started MyLine successfully")
else:
    Yprint("Started MyLine with missing source files")
    Yprint("Type \"myline check files\" for detailed informations")
Wprint("")
Wprint("Checking for restorable Changes...")
if check_temp_saves():
    Yprint("Found restorable Changes")
    Yprint("Type \"myline restore changes\" to restore Changes from last Session")
elif not check_temp_saves():
    Gprint("No restorable Changes Found")
Wprint("")
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

def send_json(file_path, thing_to_dump_man_these_variable_names_sucks_to_hard_who_in_the_world_had_this_motherfucking_idea_i_just_wanted_to_create_a_variable_named_object_and_this_silly_coding_language_thinks_it_can_forbit_me_to_do_this_i_hate_my_life_i_debugged_for_this_simple_ass_shit_thing_at_least_an_hour):
    try:
        with open(file_path, 'w') as file:
            json.dump(thing_to_dump_man_these_variable_names_sucks_to_hard_who_in_the_world_had_this_motherfucking_idea_i_just_wanted_to_create_a_variable_named_object_and_this_silly_coding_language_thinks_it_can_forbit_me_to_do_this_i_hate_my_life_i_debugged_for_this_simple_ass_shit_thing_at_least_an_hour, file, indent=4)
            return True
    except Exception:
            return False

def resolve_manufacturer(manufacturer_data):
    for company_id in manufacturer_data:
        if company_id in company_ids:
            return company_ids[company_id]
    return None

def test_connection(host="8.8.8.8", port=53, timeout=3):
    """Probe TCP connectivity and always close the socket (issue #34)."""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        Gprint(f"Successfully pinged {host} on {port}")
    except Exception as e:
        Rprint(f"Can't reach {host}. error: {e}")
    finally:
        if sock is not None:
            try:
                sock.close()
            except Exception:
                pass

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

def auto_save():
    if send_json(file_data_temp_json, data) == False:
        Rprint("Failed Auto-Save")

def myline_restore_changes(flags):
    Yprint("Restoring last Session")
    try:
        global data
        data = temp_data
    except Exception as e:
        Yprint(f"Can't Restore Changes: {e}")

def data_get_i(flags):
    parameter = flags[0]
    value = flags[1]
    found = False
    try:
        for i in data:
            field_value = i.get(parameter, "")
            if isinstance(field_value, str) and value.lower() in field_value.lower():
                found = True
                Gprint("Found >>\"" + parameter + "\" contains " + "\"" + str(value) + "\"<< under index " + str(data.index(i)) + " where value is \"" + str(data[data.index(i)][parameter]) + "\"")
        if not found:
            Rprint("nothing found under >>\"" + parameter + "\" contains " + "\"" + str(value) + "\"<<")
    except KeyError:
        Rprint("There is no parameter called >>" + parameter + "<<")

def is_filled_value(value):
    """Return whether a field contains an explicit, non-empty value."""
    if isinstance(value, bool):
        return True

    return value not in ("", 0, {}, [])


def data_head_f(flags):
    index = flags[0]

    for key, value in data[int(index)].items():
        if is_filled_value(value):
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
                message = key + " >>> " + str(value)
                GGprint(message)
            elif isinstance(value, list):
                if value != []:
                    GGprint(key + ":")
                    for i in data[int(index)][key]:
                        GGprint(f"> >>> {i}")
            elif isinstance(value, dict):
                if value != {}:
                    message = []
                    for sub_key, sub_value in data[int(index)][key].items():
                        if is_filled_value(sub_value):
                            message_entry = "> " + sub_key + " >>> " + str(sub_value)
                            message.append(message_entry)
                    if message != []:
                        GGprint(key + ":")
                        for i in message:
                            GGprint(i)

def data_head_raw(flags):
    index = flags[0]

    for key, value in data[int(index)].items():
        if is_filled_value(value):
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
                message = key + " >>> " + str(value)
                GGprint(message)
            elif isinstance(value, list):
                if value != []:
                    GGprint(key + ":")
                    for i in data[int(index)][key]:
                        GGprint(f"> >>> {i}")
            elif isinstance(value, dict):
                if value != {}:
                    GGprint(key + ":")
                    for sub_key, sub_value in data[int(index)][key].items():
                        if is_filled_value(sub_value):
                            message = "> " + sub_key + " >>> " + str(sub_value)
                            GGprint(message)
                        else:
                            message = "> " + sub_key + " >>> " + str(sub_value)
                            RRprint(message)
        else:
            message = key + " >>> " + str(value)
            RRprint(message)

def data_post_a(flags):
    if send_json(file_data_json, data) == False:
        Rprint("Can't POST data as data.json")

    if send_json(file_data_temp_json, []) == False:
        Rprint("Failed clearing Auto-Save Cache.")

def _coerce_write_value(value):
    """Convert a CLI write value from string to a JSON-friendly native type.

    Command flags always arrive as strings. Without coercion, ``data WRITE t``
    stores numbers as strings and breaks numeric comparisons against values
    loaded from JSON (issue #44).
    """
    if not isinstance(value, str):
        return value
    lowered = value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in ("null", "none"):
        return None
    # Integers first so "42" stays int; floats for values with a decimal point.
    try:
        if value.strip().startswith(("+", "-")):
            body = value.strip()[1:]
        else:
            body = value.strip()
        if body.isdigit():
            return int(value.strip())
        return float(value.strip())
    except ValueError:
        return value


def data_write_t(flags):
    index = int(flags[0])
    parameter = flags[1]
    value = _coerce_write_value(flags[2])
    data[index][parameter] = value
    auto_save()
    
def data_inspect_struc(flags):
    for i in data[0]:
        Wprint(i)

def data_inspect_count(flags):
    Wprint(f"Counted {len(data)} Objects in data")

def net_pg_uop(flags):
    test_connection(flags[0], int(flags[1]))

def ble_head_devs(flags):
    # Accept "raw" / "loop" in either flag position (issue #50).
    normalized = [str(f).lower() for f in flags if f is not None and str(f) != ""]
    show_none = "raw" in normalized

    if "loop" in normalized:
        stop_event = threading.Event()
        listener = threading.Thread(target=wait_for_stop, args=(stop_event,), daemon=True)
        listener.start()

        while not stop_event.is_set():
            asyncio.run(scan(1.0, show_none))
            Wprint("")
    else:
        asyncio.run(scan(5.0, show_none))

def myline_help_c(flags):
    YYprint("For explanations visit the GitHub page:")
    YYprint("github.com/hoffmann-paul/myline/blob/main/README.md")
    YYprint("")
    YYprint("All Commands:")

    for i in commands:
        for j in commands[i]:
            for k in commands[i][j]:
                YYprint(f"{i} {j} {k}")

def myline_help_info(flags):
    Wprint("MyLine")
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

def kill(flags):
    if flags[0] != "f":
        with open(file_data_json, 'r') as file:
            saved_data = json.load(file)
        if saved_data != data:
            Rprint("Unsaved Changes between data and data.json")
            Rprint("Killing process is canceled...")
        else:
            Gprint("No Unsaved Changes")
            RRprint("Kill MyLine...")
            sys.exit()
    elif flags[0] == "f":
        RRprint("Killing MyLine...")
        sys.exit() 

def data_write_post(flags):
    data_write_t(flags)
    data_post_a(flags)

def add_cmd_to_history(cmd):
    history.append(cmd)
    
    if send_json(file_cmdhistory_json, history) == False:
        Rprint(f"Can't add {cmd} to cmdhistory.json")
    
def myline_history_get(flags):
    if history != []:
        for i in history:
            if i.endswith("::valid"):
                Gprint(i)
            elif i.endswith("::invalid"):
                Yprint(i)
    else:
        Rprint("No command history found")

def myline_history_clear(flags):
    global history
    if send_json(file_cmdhistory_json, []):
        Rprint(f"Command history cleared successfully")
        history = []
    else:
        RRprint("Can't Clear History")

def data_card_new(flags):
    index = len(data)
    Wprint(f"Index for new Data Record: {index}")
    new_card = {}
    for p in data[0]:
        now = datetime.datetime.now()
        print(f"\033[34m@MyLine {version} [{now.strftime('%H:%M:%S')}] {p} >>> ", end="")
        value = input()
        entry = {p: value}
        new_card.update(entry)
    data.append(new_card)
    Gprint(f"Created New Data Record at index {index}")

def data_card_delete(flags):
    data.pop(int(flags[0]))
    Rprint(f"Popped Data Record at index {flags[0]}")

def myline_help_paths(flags):
    Wprint(f"data file: {file_data_json}")
    Wprint(f"cmddata file: {file_cmddata_json}")
    Wprint(f"company_ids file: {file_company_ids_json}")
    Wprint(f"cmdhistory file: {file_cmdhistory_json}")
    Wprint(f"data_temp file: {file_data_temp_json}")

def myline_check_files(flags):
    files = {
        "cmddata.json": loaded_cmddata_json,
        "cmdhistory.json": loaded_cmdhistory_json,
        "company_ids.json": loaded_company_ids_json,
        "data_temp.json": loaded_data_json,
        "data.json": loaded_data_json
    }
    for file_name in files:
        if files[file_name]:
            Gprint(f"Loaded {file_name} successfully")
        else:
            RRprint(f"An error occurred while trying to read {file_name}")
        
def repeat_last_cmd(flags):
    if history != []:
        cmd = history[-1]
        if cmd.endswith("::valid"):
            cmd = cmd.replace(" ::valid", "")
            try:
                func = globals()[cmd]
                func(flags)
            except Exception:
                Rprint("You can't repeat this command")
    else:
        Rprint("No command history found")

def data_get_im(flags):
    try:
        amount = int(flags[0]) -1
    except Exception:
        RRprint("Index Amount must me an Integer")
        return
    index_list = []
    parameter = input("parameter >>> ")
    value = input("value >>> ")
    found = False
    try:
        for i in data:
            field_value = i.get(parameter, "")
            if isinstance(field_value, str) and value.lower() in field_value.lower():
                found = True
                Gprint(str(data.index(i)) + " is working for all conditions")
                index_list.append(str(data.index(i)))
        if not found:
            Rprint("nothing works for all conditions")
    except KeyError:
        Rprint("There is no parameter called >>" + parameter + "<<")
    for a in range(amount):
            parameter = input("parameter >>> ")
            value = input("value >>> ")
            found = False
            try:
                for i in data:
                    field_value = i.get(parameter, "")
                    if isinstance(field_value, str) and value.lower() in field_value.lower():
                        found = True
                        Gprint(str(data.index(i)) + " is working for all conditions")
                        index_list.append(str(data.index(i)))
                if not found:
                    Rprint("nothing works for all conditions")
                    break
            except KeyError:
                Rprint("There is no parameter called >>" + parameter + "<<")

commands = {
    "data": {
        "GET": {
            "i": data_get_i,
            "iM": data_get_im
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
        "card": {
            "new": data_card_new,
            "delete": data_card_delete
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
            "info": myline_help_info,
            "paths": myline_help_paths
        },
        "history": {
            "GET": myline_history_get,
            "clear": myline_history_clear
        },
        "check": {
            "changes": myline_check_changes,
            "files": myline_check_files
        },
        "restore": {
            "changes": myline_restore_changes
        }
    }
} 

fast_commands = {
    "kill": kill,
    "last": repeat_last_cmd
}


def _all_command_keywords():
    """Return the union of all known top-level command keywords."""
    return list(commands.keys()) + list(fast_commands.keys())


def _complete_sub_keywords(keyword, prefix):
    """Return the sub-keywords available for ``keyword`` matching ``prefix``."""
    if keyword in fast_commands:
        return []
    sub = commands.get(keyword, {})
    return [k for k in sub.keys() if k.startswith(prefix)]


def _complete_sub_sub_keywords(keyword, sub_keyword, prefix):
    """Return the leaf command names under ``keyword sub_keyword``."""
    if keyword in fast_commands:
        return []
    sub = commands.get(keyword, {})
    leaves = sub.get(sub_keyword, {})
    return [k for k in leaves.keys() if k.startswith(prefix)]


def _line_completer(text, state):
    """readline completer for the MyLine REPL.

    Walks the words *before* the current token and returns the ``state``-th
    candidate matching ``text``. ``get_begidx()`` is important here: the line
    buffer already contains the partial token, so counting the whole buffer
    would mistake ``da<Tab>`` for a sub-command lookup.

    Returns ``None`` when no candidates match (which makes readline
    beep instead of inserting whitespace).
    """
    if readline is None:  # pragma: no cover - Windows without pyreadline
        return None
    try:
        line = readline.get_line_buffer()
        begin = readline.get_begidx()
        before_current = line[:begin]
        typed = shlex.split(before_current) if before_current.strip() else []
        prefix = text or ""
        word_index = len(typed)
        if word_index == 0:
            candidates = [k for k in _all_command_keywords() if k.startswith(prefix)]
        elif word_index == 1:
            candidates = _complete_sub_keywords(typed[0], prefix)
        elif word_index == 2:
            candidates = _complete_sub_sub_keywords(typed[0], typed[1], prefix)
        else:
            # Flags / paths — no command completion at this depth.
            candidates = []
        if 0 <= state < len(candidates):
            return candidates[state]
        return None
    except Exception:
        # Never let a completion failure crash the REPL.
        return None


def _readline_tab_binding(readline_module):
    """Return the Tab binding syntax for GNU readline or macOS libedit."""
    backend = getattr(readline_module, "backend", "")
    module_doc = getattr(readline_module, "__doc__", "") or ""
    if backend == "editline" or "libedit" in module_doc.lower():
        return "bind ^I rl_complete"
    return "tab: complete"


def _install_completer():
    """Wire the MyLine completer into readline (best-effort).

    The Tab binding syntax differs across readline implementations:

      * GNU readline (Linux): ``tab: complete``
      * libedit / NetBSD editline (macOS): ``bind ^I rl_complete``

    We try the syntax chosen by :func:`_readline_tab_binding` first,
    then fall back to the alternative so a misdetected backend (older
    Python, an unusual ``readline`` shim) still gets Tab-bound. Without
    a successful bind the Tab key is not intercepted and the terminal
    passes the literal character through, which on macOS appears as a
    stray ``[`` at the start of the line.
    """
    if not _READLINE_AVAILABLE or args.no_completion:
        return
    try:
        readline.set_completer(_line_completer)
        primary = _readline_tab_binding(readline)
        fallback = (
            "tab: complete" if primary == "bind ^I rl_complete"
            else "bind ^I rl_complete"
        )
        for binding in (primary, fallback):
            try:
                readline.parse_and_bind(binding)
                break
            except Exception:
                # Try the next syntax.
                continue
    except Exception:
        # readline can raise on broken TERM / very minimal builds; the
        # REPL stays usable even if Tab is just a no-op.
        pass


_install_completer()

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
        if keyword in fast_commands:
            flags = parts[1:]
            fast_commands[keyword](flags)
            add_cmd_to_history(f"{keyword} ::valid")
        elif keyword in commands and sub_keyword in commands[keyword] and sub_sub_keyword in commands[keyword][sub_keyword]:
            commands[keyword][sub_keyword][sub_sub_keyword](flags)
            add_cmd_to_history(f"{keyword}_{sub_keyword}_{sub_sub_keyword} ::valid")
        else:
            RRprint(f">>{raw}<< isn't a valid command")
            add_cmd_to_history(f"{keyword}_{sub_keyword}_{sub_sub_keyword} ::invalid")
    except (ValueError, IndexError, KeyError, TypeError) as e:
            # Normal user input mistakes — don't ask for a GitHub issue 
            RRprint(f"Input error: {e}")
    except Exception as e:
            RRprint(f"Unexpected Error: {e}")
            RRprint("Please open an issue on GitHub")
    Wprint("")
