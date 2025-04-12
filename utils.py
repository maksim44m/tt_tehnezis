from pathlib import Path
from typing import Union

import pandas as pd
from pandas import DataFrame


async def read_xlsx(file_path: str | Path) -> Union[DataFrame, str]:
    try:
        return pd.read_excel(file_path)
    except Exception as e:
        return f'ERROR: {e}'


