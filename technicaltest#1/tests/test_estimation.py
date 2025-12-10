import pandas as pd
from pathlib import Path
from src.estimation_script import first_numeric_col

def test_first_numeric_col_temp():
    df = pd.DataFrame({'Date': ['2020-01-01'], 'Price': [10.0]})
    assert first_numeric_col(df) == 'Price'
