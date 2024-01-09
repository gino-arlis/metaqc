import pandas as pd
from pathlib import Path


def ingest_csv():
    data_file = Path('..')/'data'/'test_data'/'savedrecs.txt'
    df = pd.read_csv(data_file, sep='\t')

    dict_info = get_wos_labels_dict()
    df = df.rename(columns=dict_info)

    return df


def get_wos_labels_dict():
    wos_keys = Path()/'wos_columns_keys.txt'
    crs = open(wos_keys, "r")
    dict_info = [ raw.strip().split() for raw in crs ]  
    dict_info = [item for item in dict_info if item!=[]]
    pairs = []

    for i in range(int(len(dict_info)/2)):
        pairs.append((dict_info[2*i][0],' '.join(dict_info[2*i+1])))
        
    dict_info = dict()
    for label,meaning in pairs:
        dict_info[label] = meaning

    dict_info['PT'] = 'Publication Type'
    dict_info['OI'] = 'ORCID Identifier'
    dict_info['Z9'] = 'Total Times Cited Count'
    return dict_info