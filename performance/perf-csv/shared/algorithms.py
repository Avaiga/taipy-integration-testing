import pandas as pd
from dataclasses import dataclass

def algorithm(df: pd.DataFrame) -> pd.DataFrame:
    return df

@dataclass
class Row:
    id: int
    age: int
    rating: float