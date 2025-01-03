from datetime import date, datetime
from pathlib import Path

import pandas as pd

from src.config import DATA_FOLDER

MONTHS_CA = [
    "gener",
    "febrer",
    "març",
    "abril",
    "maig",
    "juny",
    "juliol",
    "agost",
    "setembre",
    "octubre",
    "novembre",
    "desembre",
]

MONTHS_EN = [
    "january",
    "february",
    "march",
    "april",
    "may",
    "june",
    "july",
    "august",
    "september",
    "october",
    "november",
    "december",
]


def load_csv(filepath: Path):
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError as err:
        raise err


def export_csv(data: pd.DataFrame, filepath: Path):
    filepath.parent.mkdir(exist_ok=True, parents=True)
    data.to_csv(filepath, index=False)


def load_file(date: date, filename: str):
    month_name = date.strftime("%B").lower()
    year = date.year
    filepath = DATA_FOLDER / str(year) / str(month_name) / filename

    return filepath


def get_previous_file(date: date, filename: str):
    current_month_name = date.strftime("%B").lower()
    current_year = date.year
    year_folder = DATA_FOLDER / str(current_year)
    years = list(range(current_year - 10, current_year + 1))[::-1]
    months = MONTHS_EN[::-1]

    for year in years:
        for month_i, month in enumerate(months, start=1):
            month_path = DATA_FOLDER / str(year) / month
            if year == current_year and (13 - month_i) >= date.month:
                continue
            if month_path.exists() and month_path.is_dir():
                return month_path / filename, datetime(year, 13 - month_i, 1)
    return None, None


def get_month_name(month: int, language: str = "catala"):
    catala = [
        "gener",
        "febrer",
        "març",
        "abril",
        "maig",
        "juny",
        "juliol",
        "agost",
        "setembre",
        "octubre",
        "novembre",
        "desembre",
    ]

    if language == "catala":
        return catala[month - 1]
    else:
        return datetime(2024, month, 1).strftime("%B").lower()
