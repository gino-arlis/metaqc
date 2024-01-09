import pandas as pd
from pathlib import Path


def ingest_csv():
    data_file = Path('..')/'data'/'test_data'/'savedrecs.txt'
    df = pd.read_csv(data_file, sep='\t')
    return df