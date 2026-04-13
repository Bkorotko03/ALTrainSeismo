# helper script for writing interactive guy
import sys

def _get_int(prompt, default, min_value=None):
    raw = input(prompt).strip()
    if raw == "":
        return default
    try:
        val = int(raw)
        if min_value is not None and val < min_value:
            print(f"Using default {default} (value must be >= {min_value}).")
            return default
        return val
    except ValueError:
        print(f"Using default {default} (invalid integer).")
        return default

def _get_float(prompt, default, min_value=None):
    raw = input(prompt).strip()
    if raw == "":
        return default
    try:
        val = float(raw)
        if min_value is not None and val < min_value:
            print(f"Using default {default} (value must be >= {min_value}).")
            return default
        return val
    except ValueError:
        print(f"Using default {default} (invalid number).")
        return default

def _get_str(prompt, default):
    raw = input(prompt).strip()
    if raw == "":
        return default
    elif (raw == "lin") or (raw == "log"):
        return raw
    else:
        print('Input lin or log')
        sys.exit()

def _get_bool(prompt, default=True):
    raw = input(prompt).strip().lower()
    if raw == "":
        return default
    elif raw in ("y", "yes"):
        return True
    elif raw in ("n", "no"):
        return False
    else:
        print("Input y or n.")
        sys.exit()