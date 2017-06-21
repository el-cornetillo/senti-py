"""
    Crawler to get the comments and ratings from sensaCine
    (http://www.sensacine.com)
"""

import bs4 ## BeautifulSoup4, for html extraction
import urllib.request
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

## Hard-coded constants to remove from comments
## USE .strip() !!!
uglySensaCineTab = "\n                    \n                                            "
Tab = '\n'

suffixUrl = "criticas-espectadores/"
prefixUrl = "http://www.sensacine.com"
topBaseUrl = "http://www.sensacine.com/peliculas/mejores/nota-espectadores/"
commentsPerPage = 10
numberOfCommentsFetched = 0

def getComments(htmlUrl):
    '''
        Extract the (comments,ratings) for a given movie
        :param htmlUrl: Url of the reviews page of a movie
        :return : comments and ratings as a Python list
    '''
    
    commentsList = []
    ratingsList = []
    
    htmlContent = urllib.request.urlopen(htmlUrl).read()
    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')

    numberOfComments = re.search('[0-9]+',soup.find('h2', attrs={"class": "titlebar-title titlebar-title-md"}).text).group(0)
    numberOfPages = (int(numberOfComments) // commentsPerPage) + 1
    print('Fetching %d comments' % int(numberOfComments))
    global numberOfCommentsFetched
    numberOfCommentsFetched += int(numberOfComments)

    def getCommentsOfPage(htmlUrl, pageNumber, commentsList, ratingsList):
        ## Intern function because comments might occupy several pages (if more than 10 comments)

        htmlUrl += '?page=%d' % pageNumber
        print('doing page %d of %d' % (pageNumber,numberOfPages))
        numberOfCommentsOnPage = 10 if pageNumber!=numberOfPages else int(numberOfComments)%commentsPerPage
        htmlContent = urllib.request.urlopen(htmlUrl).read()
        soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
        
        commentsList += [emoji_pattern.sub(r'',elem.text).replace(uglySensaCineTab,'').replace(Tab,'') for elem in \
                        soup.findAll('p', attrs={'itemprop': 'description'})]

        ratingsList += [float(elem.text[-3:].replace(',','.')) for elem in \
                        soup.findAll('span', attrs={'class': 'stareval-note'}, limit=numberOfCommentsOnPage)]
    for k in range(numberOfPages):
        getCommentsOfPage(htmlUrl, k+1, commentsList, ratingsList)
        
    return list(zip(commentsList, ratingsList)), numberOfCommentsFetched

def getListOfMovies(htmlUrl):
    '''
        Extract the urls of the movie pages from the top movies of sensaCine
        :param htmlUrl: URL of the page to scrap from
        :return moviesList: urls of the movies presented on that page as a Python list
    '''

    htmlContent = urllib.request.urlopen(htmlUrl).read()
    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
    
    moviesList = [prefixUrl + elem['href'] + suffixUrl for elem in soup.findAll('a', attrs={'class': 'no_underline'})]
    
    return moviesList

def loopOver(pageIndexes, verbose=True):
    '''
        The function that actually scraps the comments from sensaCine
        :param pageIndexes: list/array, indexes of the pages to scrap from
        :param verbose: if set True prints the progression of the loop (recommended)
        :return commentsData: (comments,ratings) scrapped from the given pages
    '''

    commentsData = []
    for pageIndex in pageIndexes:
        if verbose:
            print('Processing page number %d' % pageIndex)
        htmlUrl = topBaseUrl + '?page=%d' % pageIndex
        moviesList = getListOfMovies(htmlUrl)
        if verbose:
            print(' ')
            print('Got the list of all the movies of page %d' % pageIndex)
            counter = 1
            
            
        for movieUrl in moviesList:
            try:
                commentsOfPage, totalReviews = getComments(movieUrl)
                commentsData += commentsOfPage
                if verbose:
                    print('Fetched data from movie %d of 20' % counter)
                    print('--------------DataSet now has %d reviews' % totalReviews)
                    counter = counter + 1
            except Exception:
                print('Problem with movie %d' % counter)
                counter = counter + 1
                pass
            
    return commentsData

def createChunks():
    chunks = [np.arange(10*i + 1,10*(i+1) + 1) for i in range(10)]
    chunks.append(np.arange(101,151))
    chunks.append(np.arange(151,201))
    chunks += [np.arange(100*i + 1,100*(i+1) + 1) for i in np.arange(2,26)]
    chunks.append(np.arange(2601,2638))
    return chunks
    
def main():
    ''''
        Loop over all the movie pages, save the results as a pandas DataFrame and write into to a csv.
        Proceed chunk by chunk, to save memory.
        :param :
        :return void:
    '''
    chunksIndexes=createChunks()
    for chunk in chunksIndexes:
        commentsData = loopOver(chunk,verbose=True)
        df = pd.DataFrame(data = commentsData, columns = ['Comment', 'Rating'])
        df.to_csv(path='./commentsData'+('%d-%d.csv' % (chunk[0], chunk[-1])), index=False, sep=';')