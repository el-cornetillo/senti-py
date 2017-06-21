'''
    Crawls through the website asihablamos.com to gather the list of 
    argentine words and expressions, along with their definition, synonyms and exemples.
    Will help to build the classifier of sentiment analysis, since prediction can be performed 
    on the definitions and then be associated to the argentine words.
'''

import bs4
import urllib.request
import pandas as pd
import re
from tqdm import tqdm ## Package copado to print progression of calculus 
                      ##(and integrates with pandas). FACULTATIVE, COMMENT IF THE PACKAGE ISNT INSTALLED 

urlWords = 'http://www.asihablamos.com/word/pais/ar/'

def get_infos(htmlUrl):
    '''
        Gets the informations about a given word.
        :param htmlUrl: Url of the word page
        :return definition: String, definition of the word/expression
        :return exemple: String, an exemple of use of the word/expression
        :return synonyms: List, contains the synonymns
    '''
    htmlContent = urllib.request.urlopen(htmlUrl).read()
    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')

    argentinaDiv = soup.findAll('div', attrs={'class': 'definicion'})[0]
    soupDiv = bs4.BeautifulSoup(str(argentinaDiv), 'html5lib')
    listDiv = soupDiv.findAll('div')
    
    definition = listDiv[2].next
    exemple = listDiv[3].next
    
    synonyms = [re.search('>.+<',str(i)).group(0)[1:-1] for i in soupDiv.findAll('a', attrs= {'class': 'btn'})]
    
    return definition, exemple, synonyms

def replaceAccents(word):
    '''
        Convenience function to handle the probles of URL encoding with UTF-8
    '''
    word = word.replace('%C3%AD','í')
    word = word.replace('%C3%B3','ó')
    word = word.replace('%C3%B2', 'ò')
    word = word.replace('%C3%B1', 'ñ')
    word = word.replace('%C3%A9', 'é')
    word = word.replace('%C3%A8', 'è')
    word = word.replace('%C3%A1', 'á')
    
    return word


def getWordUrls(htmlUrl):
    '''
        Get the list of the URLS to the different words and expressions 
        of the argentine spanish
    '''
    htmlContent = urllib.request.urlopen(htmlUrl)
    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
    words = soup.findAll('a', attrs={'class': 'btn btn-lg col-sm-4 col-xs-12'})

    return [(re.search('>.+<',str(word)).group(0)[1:-1], 'http://www.asihablamos.com/'+ word['href']) for word in words]


#Crawling is done here

wordsParsed = getWordUrls(urlWords)
df = pd.DataFrame(data = wordsParsed , columns = ['Word', 'Url'])
df['Url'] = df['Url'].apply(lambda x : x.replace('com//', 'com/'))

## if tqdm is installed
tqdm.pandas(desc="progress-bar")
df['Definition'], df['Example'], df['Synonyms'] = zip(*df['Url'].progress_apply(lambda x : get_infos(x)))

## if tqdm isnt installed, uncomment here and comment above

#df['Definition'], df['Example'], df['Synonyms'] = zip(*df['Url'].apply(lambda x : get_infos(x)))

df.head(30)
