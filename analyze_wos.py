from collections import Counter
import pandas as pd
import plotly.express as px
import pickle
from collections import defaultdict

#color_discrete_map= defaultdict('yellow')
color_discrete_map = {'USA':'blue',
                      'Canada': 'cyan',
                      'Germany': 'lightblue',
                      'Peoples R China': 'red',
                      'Austria': 'green',
                      'Switzerland': 'brown'}
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
