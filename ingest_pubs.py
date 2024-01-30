import pandas as pd
from pathlib import Path
import math
from collections import defaultdict
from pprint import pprint


# Ingestion functions

def get_data_folder_data(data_folder):
    
    dataframes = list()
    for file in data_folder.glob('*.txt'):
        file_df = ingest_csv_file(file)
        print('file: ',file,'Number of papers: ', len(file_df))
        dataframes.append(file_df)
  
    df = pd.concat(dataframes, axis=0)
    print('Total number of papers: ',len(df))
    return df


def ingest_csv_file(data_file):
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
    dict_info['ID'] = 'Keywords Plus'

    return dict_info


def get_dicts(df):
    
    authors_d = dict()
    papers_d = dict()
    institutions_d = dict()

    for idx,record in df.iterrows():

        # Construct the authors dictionary
        print('Before adding author for ', idx)
        authors_d = add_authors(authors_d, record)

        # Construct the papers dictionary
        papers_d = add_papers(papers_d, record)

        # Construct the institutions related dictionary
        institutions_d = add_institutions(institutions_d, record)

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
    print('*', record)
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


# Papers related functions
def add_papers(papers_d, record):
    wos_identifier = record['Accession Number']
    
    authors_list = record['Author Full Name'].split(';')
    authors_list = [item.strip(' ') for item in authors_list]

    publication_type = record['Publication Type']
    title = record['Document Title']

    publication_name = record['Publication Name']
    abstract = record['Abstract']
    cited_references = record['Cited References']

    publication_date = record['Publication Date']
    year_published = record ['Year Published']
    doi = record['Digital Object Identifier (DOI)']

    institutions = get_record_institutions(record)
    keywords = record['Author Keywords']
    keywords_plus = record['Keywords Plus'] 
    funding = record['Funding Agency and Grant Number']

    papers_d[wos_identifier] = {'wos_identifier': wos_identifier,
                                'authors': authors_list,
                                'publication type': publication_type,
                                'title':title,
                                'publication name':publication_name,
                                'abstract': abstract,
                                'cited references': cited_references,
                                'publication date': publication_date,
                                'publication year': year_published,
                                'doi': doi,
                                'institutions': institutions,
                                'keywords': keywords,
                                'keywords plus': keywords_plus,
                                'funding': funding
                                }

    return papers_d


def get_record_institutions(record):
    authors_inst_dict= get_author_inst_dict(record)
    institutions_ll = list(authors_inst_dict.values())
    institutions = list()
    for sub_list in institutions_ll:
        for item in sub_list:
            institutions.append(item[1])
    institutions=list(set(institutions))

    return institutions


# Institutions related functions
def add_institutions(institutions_d, record):
    wos_identifier = record['Accession Number']
    institutions = get_record_institutions(record)
    for institution in institutions:

        if institution not in institutions_d:
            country = institution.split(',')[-1].strip(' ')
            if ' USA' in country:
                country='USA'
            institutions_d[institution]={'institution name': institution,
                                         'country': country,
                                         'papers': [wos_identifier]}
        else:
            institutions_d[institution]['papers'].append(wos_identifier)
    return institutions_d

# Auxiliary functions
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


def sample_dict(target_d):
    import random
    from pprint import pprint

    random_element = random.choice(list(target_d.keys()))
    print(random_element)
    pprint(target_d[random_element])

    return