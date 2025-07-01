import json
import pandas as pd

def is_valid_json_file(file):
    try:
        if file is None:
            return False
        if hasattr(file, "seek"):
            file.seek(0)
        json.load(file)
        if hasattr(file, "seek"):
            file.seek(0)
        return True
    except Exception:
        return False

def is_valid_csv_file(file):
    try:
        if file is None:
            return False
        if hasattr(file, "seek"):
            file.seek(0)
        pd.read_csv(file, nrows=1)
        if hasattr(file, "seek"):
            file.seek(0)
        return True
    except Exception:
        return False
