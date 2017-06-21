import re
import bs4
from urllib.request import Request, urlopen
import json

## Constants
pathVerbs = "Classifier/dataset/verbosCommunes.txt"
pathConjug = "Classifier/dataset/dictConjug.json" ## XXX : to fill

def replaceAccents(word):
    word = word.replace('í','i')
    word = word.replace('ó','o')
    word = word.replace('ò','o')
    word = word.replace('ñ','n')
    word = word.replace('é','e')
    word = word.replace('è','e')
    word = word.replace('á','a')
    word = word.replace('à','a')
    word = word.replace('ü','u')
    word = word.replace('ú','u')
    word = word.replace('ö','o')
    word = word.replace('ë','e')
    word = word.replace('ï','i')
    
    return word

removeVerbs = ['nadar','unir','dar']
appendVerbs = ['mentir','estafar','cambiar','ganar','recibir','responder','demorar','tardar','caer']
listOfVerbs = [e.split()[0].lower() for e in open(pathVerbs).readlines() if e.split()[0].lower() not in removeVerbs]

for verb in appendVerbs:
    if verb not in listOfVerbs:
        listOfVerbs.append(verb)

dictConjug = {}
for v in listOfVerbs:
        dictConjug[v] = [replaceAccents(e.text.lower()).replace(' ','_') for e in \
                     bs4.BeautifulSoup(urlopen(Request('http://fr.bab.la/conjugaison/espagnol/'+v, \
                    headers={'User-Agent': 'Mozilla/5.0'})).read(), 'html5lib').findAll('div', {"class": 'conj-result'})][:-1]

with open(pathConjug, 'w') as f:
    json.dump(dictConjug, f, sort_keys=True, indent=4)   