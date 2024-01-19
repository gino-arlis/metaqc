from collections import Counter
import itertools
import pickle
from collections import defaultdict

import pandas as pd
import plotly.express as px
import networkx as nx
import matplotlib.pyplot as plt


color_discrete_map= defaultdict(lambda:'black')
color_discrete_map = {'USA':'blue',
                      'Canada': 'cyan',
                      'Germany': 'lightblue',
                      'Peoples R China': 'red',
                      'Austria': 'green',
                      'Switzerland': 'brown',
                      'Singapore':'orange'}

def load_dictionaries():
    with open('authors_d.pickle', 'rb') as handle:
        authors_d = pickle.load(handle)

    with open('papers_d.pickle', 'rb') as handle:
        papers_d = pickle.load(handle)

    with open('institutions_d.pickle', 'rb') as handle:
        institutions_d = pickle.load(handle)

    return authors_d, papers_d, institutions_d


def get_prolific_authors(authors_d):
    
    prolific_authors=list()

    for author in authors_d:
        # number of papers
        n_papers = len(authors_d[author]['papers'])

        # Country
        countries= list()
        for item in authors_d[author]['institution history']:
            institution = item[1]
            country = institution.split(',')[-1].strip(' ')
            if ' USA' in country:
                country='USA'
            countries.append(country)
        #print(countries)
        if len(countries)==0:
            majority_country='None'
        else:
            majority_country = Counter(countries).most_common()[0][0]

        prolific_authors.append((author, n_papers, majority_country) )
    
    prolific_authors = sorted(prolific_authors, 
                              key = lambda item: item[1], 
                              reverse=True)

    return prolific_authors


def get_fig_prolific_authors(authors_d, n=10):
    prolific_authors = get_prolific_authors(authors_d)
    prolific_authors = prolific_authors[0:n]

    # Create df for plotly
    author = [item[0] for item in prolific_authors]
    count = [item[1] for item in prolific_authors]
    country = [item[2] for item in prolific_authors]

    df = pd.DataFrame({'author': author, 
                       'count': count, 
                       'country':country})
    

    fig = px.bar(df, 
                 x='author', 
                 color = 'country', y= 'count', 
                 labels = {'count': 'number of papers'},
                 color_discrete_map= color_discrete_map,
                 title = 'Most prolific authors')
    
    fig.update_layout( xaxis={'categoryorder':'total descending', 
                              'categoryarray':df.index})
    
    return fig


def get_prolific_institutions(institutions_d):

    prolific_institutions = list()

    for institution in institutions_d:
        # number of papers
        n_papers = len(institutions_d[institution]['papers'])

        # Country
        #print(institutions_d[institution])
        country = institutions_d[institution]['country']

        prolific_institutions.append((institution, n_papers, country))
    prolific_institutions = sorted(prolific_institutions, 
                                   key= lambda item: item[1], 
                                   reverse=True)

    return prolific_institutions


def get_fig_prolific_institutions(institutions_d, n=10):

    prolific_institutions = get_prolific_institutions(institutions_d)
    prolific_institutions = prolific_institutions[0:n]

    # Create df for plotly
    institution = [item[0] for item in prolific_institutions]
    institution_short_name=[item[0:15] for item in institution]

    count = [item[1] for item in prolific_institutions]
    country = [item[2] for item in prolific_institutions]

    df = pd.DataFrame({'institution': institution, 
                       'institution_short_name': institution_short_name,
                       'count': count, 
                       'country':country})
    

    fig = px.bar(df, 
                 y='institution_short_name', 
                 color = 'country', 
                 x= 'count', 
                 orientation = 'h',
                 labels = {'count': 'number of papers'},
                 color_discrete_map= color_discrete_map,
                 title = 'Most prolific institutions')
    
    fig.update_layout( yaxis={'categoryorder':'total descending', 
                              'categoryarray':df.index},
                              margin=dict(l=100))
    
    return fig


def get_inst_graph(institutions_d, cut_off = 20):
    G = nx.Graph()

    prolific_institutions = \
        get_prolific_institutions(institutions_d)
    prolific_institutions= prolific_institutions[0:cut_off]

    nodes = [item[0] for item in prolific_institutions[0:cut_off]]

    edges = list()
    for inst_1, inst_2 in itertools.combinations(nodes,2):
        inst_1_papers = set( institutions_d[inst_1]['papers'])
        inst_2_papers = set(institutions_d[inst_2]['papers'])
        inter_size = len(inst_1_papers.intersection(inst_2_papers))
        if inter_size>0:
            edges.append((inst_1,inst_2))

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    return G


def plot_inst_graph(G, institutions_d, gcc=False):

    if gcc:
        Gcc = sorted(nx.connected_components(G), 
                     key=len, 
                     reverse=True)
        G = G.subgraph(Gcc[0])

    # Define node colors
    color_map=list()
    for node in G:
        country = institutions_d[node]['country']
        if country not in color_discrete_map:
            color = 'yellow'
        else:
            color = color_discrete_map[country]
        color_map.append(color)

    # Define node sizes
    node_size = list()
    for node in G:
        size = len(institutions_d[node]['papers'])
        node_size.append(size)
    max_node = max(node_size)
    min_node = min(node_size)
    factor = (200-10)/(max_node-min_node)
    node_size = [(size-min_node)*factor+10 for size in node_size]
    
    # Define node labels
    labels={}
    for node in G:
        if len(institutions_d[node]['papers'])>9:
            labels[node]=','.join(node.split(',')[0:-2])

            
    edges=G.edges()
    weights=[4 for u,v in G.edges()]

    plt.figure(figsize=(14,14))
    nx.draw(G, 
            with_labels=True, 
            labels=labels,
            node_color=color_map, 
            font_size=10,
            font_color='darkgreen',
            node_size=node_size)
    
    plt.show()

    return