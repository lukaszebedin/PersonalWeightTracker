import json
import pandas as pd
import pathlib
import streamlit as st


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


def load_data():
    path_csv = pathlib.Path(__file__).parent.parent.resolve() / "data" / "lukas.csv"
    if 'user_data' not in st.session_state and path_csv.is_file():
        df = pd.read_csv(path_csv.as_posix(), parse_dates=['date'])
        st.session_state['user_data'] = df
        st.session_state['file_uploaded'] = True
        st.rerun()


def save_data():
    path_csv = pathlib.Path(__file__).parent.parent.resolve() / "data" / "lukas.csv"
    df = st.session_state['user_data']
    csv = df.to_csv(index=False, date_format='%Y-%m-%d %H:%M:%S')
    with open(path_csv.as_posix(), "w") as file_handle:
        file_handle.write(csv)
