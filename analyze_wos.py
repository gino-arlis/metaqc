from collections import Counter

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
    
    prolific_authors = sorted(prolific_authors, key = lambda item: item[1], reverse=True)

    return prolific_authors

