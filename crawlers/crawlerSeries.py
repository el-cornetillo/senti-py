"""
    Crawler to get the comments and ratings from sensaCine (section series)
    (http://www.sensacine.com)
"""

import bs4 ## BeautifulSoup4, for html extraction
from urllib.request import Request, urlopen
import pandas as pd
import numpy as np
import re ## for reg ex

#### CONSTANTS

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE) ## to remove emojis from reviews

uglySensaCineTab = "\n                    \n                                            "
Tab = '\n'

suffixUrl = "criticas/"
prefixUrl = "http://www.sensacine.com"
topBaseUrl = "http://www.sensacine.com/series-tv/"
commentsPerPage = 10

##Global variables
numberOfCommentsFetched = 0
commentsData = []

def getComments(htmlUrl):
    '''
        Extract the (comments,ratings) for a given serie
        :param htmlUrl: Url of the reviews page of a serie
        :return : comments and ratings as a Python list
    '''
    
    commentsList = []
    ratingsList = []
    
    req = Request(htmlUrl, headers={'User-Agent': 'Mozilla/5.0'})
    htmlContent = urlopen(req).read()
    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
    
    if 'Críticas' in [elem.text for elem in soup.findAll('span', attrs={'class': 'inactive'})]:
        numberOfComments = 0
    else:
        numberOfComments = int(re.search('[0-9]+',soup.find('h2', attrs={"class": "tt_r22"}).text).group(0))
    numberOfPages = (int(numberOfComments) // commentsPerPage) + 1
    print('Fetching %d comments' % int(numberOfComments))
    global numberOfCommentsFetched
    numberOfCommentsFetched += int(numberOfComments)

    def getCommentsOfPage(htmlUrl, pageNumber, commentsList, ratingsList):
        ## Intern function because comments might occupy several pages (if more than 10 comments)

        htmlUrl += '?page=%d' % pageNumber
        print('doing page %d of %d' % (pageNumber,numberOfPages))
        numberOfCommentsOnPage = 10 if pageNumber!=numberOfPages else int(numberOfComments)%commentsPerPage
        req = Request(htmlUrl, headers={'User-Agent': 'Mozilla/5.0'})
        htmlContent = urlopen(req).read()
        soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
        
        commentsList += [emoji_pattern.sub(r'',elem.text).replace(uglySensaCineTab,'').replace(Tab,'') for elem in \
                         soup.findAll('p', attrs={'itemprop': 'description'})]

        ratingsList += [float(elem['content']) for elem in \
                        soup.findAll('span', attrs={'itemprop': 'ratingValue'}, limit=numberOfCommentsOnPage)]
        
    if numberOfComments>0:
        for k in range(numberOfPages):
            getCommentsOfPage(htmlUrl, k+1, commentsList, ratingsList)
    
    return list(zip(commentsList, ratingsList)), numberOfCommentsFetched, numberOfComments

def getListOfSeries(htmlUrl):
    '''
        Extract the urls of the serie pages from the top series of sensaCine
        :param htmlUrl: URL of the page to scrap from
        :return moviesList: urls of the series presented on that page as a Python list
    '''

    req = Request(htmlUrl, headers={'User-Agent': 'Mozilla/5.0'})
    htmlContent = urlopen(req).read()
    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
    
    seriesList = [prefixUrl + elem['href'] + suffixUrl for elem in soup.findAll('a', attrs={'class': 'no_underline'})]
    
    return seriesList

def loopOver(pageIndexes, verbose=True):
    '''
        The function that actually scraps the comments from sensaCine
        :param pageIndexes: list/array, indexes of the pages to scrap from
        :param verbose: if set True prints the progression of the loop (recommended)
        :return commentsData: (comments,ratings) scrapped from the given pages
    '''
    global commentsData
    commentsData = []
    for pageIndex in pageIndexes:
        if verbose:
            print('Processing page number %d' % pageIndex)
        htmlUrl = topBaseUrl + '?page=%d' % pageIndex
        seriesList = getListOfSeries(htmlUrl)
        if verbose:
            print(' ')
            print('Got the list of all the series of page %d' % pageIndex)
            counter = 1
            
        for serieUrl in seriesList:
            try:
                commentsOfPage, totalReviews, newCommentsNumber = getComments(serieUrl)
                if newCommentsNumber>0:
                    commentsData += commentsOfPage
                if verbose:
                    print('Fetched data from serie %d of 20' % counter)
                    print('--------------DataSet now has %d reviews' % totalReviews)
                    counter = counter + 1
            except Exception:
                print('Problem with serie %d' % counter)
                counter = counter + 1
                pass
            
    #return commentsData

def createChunks():
    ''''
        We will proced chunk by chunk, to save memory.
        First chunks are of size 10, then 50
        :param :
        :return void:
    '''
    chunks = [np.arange(10*i + 1,10*(i+1) + 1) for i in range(10)]
    chunks.append(np.arange(101,151))
    chunks.append(np.arange(151,201))
    chunks.append(np.arange(201,285))
    return chunks
    
def main():
    ''''
        Loop over all the serie pages, save the results as a pandas DataFrame and write into to a csv.
        Proceed chunk by chunk, to save memory.
        :param :
        :return void:
    '''
    chunksIndexes=createChunks()
    for chunk in chunksIndexes:
        loopOver(chunk,verbose=True)
        df = pd.DataFrame(data = commentsData, columns = ['Comment', 'Rating'])
        df.to_csv(str('./seriesCommentsData_'+('%d-%d.csv' % (chunk[0], chunk[-1]))), index=False, sep=';')