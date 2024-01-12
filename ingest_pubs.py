import pandas as pd
from pathlib import Path
import math
from collections import defaultdict
from pprint import pprint


# Ingestion functions
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


def get_dicts(df):
    
    authors_d = dict()
    papers_d = dict()
    institutions_d = dict()

    for idx,record in df.iterrows():

        # Construct the authors dictionary
        authors_d = add_authors(authors_d, record)

        # Construct the papers dictionary

    return authors_d, papers_d , institutions_d


# Author related functions
def add_authors(authors_d, record):
    
    wos_identifier = record['Accession Number']
    authors_dicts = get_authors_dicts(record)

    #pprint(authors_dicts)
    for author_dict in authors_dicts:
        if author_dict['full name'] in authors_d:
            #print("Bingo!")
            #print('author_dict: ')
            #pprint( author_dict)
            #print('Before: ', authors_d['Passian, Ali'])
            authors_d[author_dict['full name']]['papers'].append(wos_identifier)
            #print('After: ', authors_d['Passian, Ali'])
            authors_d[author_dict['full name']]['institution history']+= \
                author_dict['institution history']
        else:
            authors_d[author_dict['full name']] = author_dict
        
    return authors_d


def get_authors_dicts(record):

    # Useful record Fields
    wos_identifier = record['Accession Number']
    
    authors_list = record['Authors'].split(';')
    authors_list = [item.strip(' ') for item in authors_list]
    
    author_full_name_list = record['Author Full Name'].split(';')
    author_full_name_list = [item.strip(' ') for item in author_full_name_list]

    authors_inst_dict = get_author_inst_dict(record)

    authors_dicts = list()
    for name, full_name in zip(authors_list, author_full_name_list):
        authors_dicts.append({'name':name, 
                             'full name':full_name, 
                             'papers':[wos_identifier],
                             'institution history':authors_inst_dict[full_name]})
        
    return authors_dicts


def get_author_inst_dict(record):
    authors_inst_dict = defaultdict(list)
    year = record['Year Published']
    
    target = record['Author Address']

    fields = no_nest_split(target)
    for field in fields:
        cut = field.find(']')
        author_list = field[1:cut].split(';')
        author_list = [item.strip(' ') for item in author_list]
        inst = field[cut+1:].strip(' ')
        for author in author_list:
            authors_inst_dict[author].append((year,inst))

    return authors_inst_dict


def no_nest_split(target):
    
    # Unfortunately the data has some nans here
    if target!=target:
        return []
    
    detect = True
    sep_indices = list()
    
    for idx, item in enumerate(target):
        if item in '[]':
            detect = not detect
        elif item==';' and detect:
            sep_indices.append(idx)
 
    split_target = list()
    start_idx = 0
    for idx in sep_indices:
        stop_idx = idx
        split_target.append(target[start_idx:stop_idx].strip(' '))
        start_idx = stop_idx+1
    split_target.append(target[start_idx:].strip(' '))
        
    return split_target