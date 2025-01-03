from datetime import datetime
from pathlib import Path

now = datetime.now()
current_month_name = now.strftime("%B").lower()
current_year = now.year

## CONFIGURATIONS
BASE_DIR = Path(__file__).parent.parent.resolve()
DATA_FOLDER = (BASE_DIR / "data").resolve()
CURRENT_YEAR_FOLDER = DATA_FOLDER / str(current_year)
CURRENT_YEAR_FOLDER.mkdir(exist_ok=True, parents=True)

CURRENT_MONTH_FOLDER = CURRENT_YEAR_FOLDER / current_month_name
CURRENT_MONTH_FOLDER.mkdir(exist_ok=True, parents=True)

# BACKUP FOLDER
BACKUP_FOLDER = ...

# Colors
COLOR_RED = "#ed4747"
COLOR_YELLOW = "#edc947"
COLOR_GREEN = "#47ed60"
COLOR_LIGHTBLUE = "#47e7ed"
COLOR_BLUE = "#4797ed"
COLOR_DARKBLUE = "#2b288f"
COLOR_GRAY = "#666666"
COLOR_PURPLE = "#9b3fd4"
COLOR_ORANGE = "#d4823f"

# Types of expenses
EXPENSE_TYPES = {
    "imprescindible": {"nom": "Imprescindible", "color": COLOR_RED},
    "oci": {"nom": "Oci", "color": COLOR_LIGHTBLUE},
    "subscripcio": {"nom": "Subscripcio", "color": COLOR_PURPLE},
    "microestalvi": {"nom": "Micro estalvi", "color": COLOR_DARKBLUE},
}

# Salari
SALARY = 1600
