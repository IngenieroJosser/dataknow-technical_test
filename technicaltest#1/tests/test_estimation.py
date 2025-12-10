import sys
from pathlib import Path

# Añadir la raíz del proyecto (technicaltest#1/) al PATH
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

import pandas as pd
from src.estimation_script import first_numeric_col

def test_first_numeric_col_temp():
    df = pd.DataFrame({'Date': ['2020-01-01'], 'Price': [10.0]})
    assert first_numeric_col(df) == 'Price'
