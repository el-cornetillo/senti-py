import bs4 ## BeautifulSoup4, for html extraction
import urllib.request
import pandas as pd
import numpy as np
import re ## for reg ex

Tab = '\n'

hiddenSuffix = "&sort=registeredDate%3Adesc"
hiddenPrefix = "https://www.pedidosya.com.ar/review?restId="
topBaseUrl = "https://www.pedidosya.com.ar/restaurantes/buenos-aires?a=echeverria%202077&lat=-34.5610193&lng=-58.45286420000002"
commentsPerPage = 10

##Global variables
numberOfCommentsFetched = 0
commentsData = []    

def getComments(htmlUrl):
    '''
        Extract the (comments,ratings) for a given movie
        :param htmlUrl: Url of the reviews page of a movie
        :return : comments and ratings as a Python list
    '''
    
    commentsList = []
    ratingsList = []
    
    req = Request(htmlUrl, headers={'User-Agent': 'Mozilla/5.0'})
    htmlContent = urlopen(req).read()

    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
    restaurantId = soup.find('div', attrs={'id': 'profileHeader'})['data-id']
    numberOfPages = int(soup.findAll('li', attrs={'data-auto': 'pagination_item'})[2].text)
    hiddenUrl = hiddenPrefix + str(restaurantId)
    
    def getCommentsOfPage(htmlUrl, pageNumber, commentsList, ratingsList):
        ## Intern function because comments might occupy several pages (if more than 10 comments)

        htmlUrl += ('&max=10&page=' + str(pageNumber) + hiddenSuffix)
        print('doing page %d of %d' % (pageNumber,numberOfPages))
        req = Request(htmlUrl, headers={'User-Agent': 'Mozilla/5.0'})
        htmlContent = urlopen(req).read()
        soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
        
        commentsList += [elem.text.replace(Tab,'') for elem in soup.findAll('p', attrs={'itemprop': 'description'})]

        ratingsList += [float(elem.text) for elem in soup.findAll('i', attrs={'class': 'rating-points'})]
        
        return len(commentsList)
        
    for k in range(numberOfPages):
        numberOfComments = getCommentsOfPage(hiddenUrl, k+1, commentsList, ratingsList)
        global numberOfCommentsFetched
        numberOfCommentsFetched += numberOfComments       
        
    return list(zip(commentsList, ratingsList)), numberOfCommentsFetched

def getListOfRestaurants(htmlUrl):
    '''
        Extract the urls of the movie pages from the top movies of sensaCine
        :param htmlUrl: URL of the page to scrap from
        :return moviesList: urls of the movies presented on that page as a Python list
    '''
    req = Request(htmlUrl, headers={'User-Agent': 'Mozilla/5.0'})
    htmlContent = urlopen(req).read()
    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
    
    restaurantsList = [elem['href'] for elem in soup.findAll('a', attrs={'class': 'arrivalName'})]
    
    return restaurantsList

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
        htmlUrl = topBaseUrl + '&page=%d' % pageIndex
        restaurantsList = getListOfRestaurants(htmlUrl)
        if verbose:
            print(' ')
            print('Got the list of all the restaurants of page %d' % pageIndex)
            counter = 1
                 
        for restaurantUrl in restaurantsList:
            try:
                commentsOfPage, totalReviews = getComments(restaurantUrl)
                commentsData += commentsOfPage
                if verbose:
                    print('Fetched data from restaurant %d of 20' % counter)
                    print('--------------DataSet now has %d reviews' % totalReviews)
                    counter = counter + 1
            except Exception:
                print('Problem with restaurant %d' % counter)
                counter = counter + 1
                pass
            
    #return commentsData
    
def main():
    ''''
        Loop over all the movie pages, save the results as a pandas DataFrame and write into to a csv.
        Proceed chunk by chunk, to save memory.
        :param :
        :return void:
    '''
    chunksIndexes=[np.arange(1,8)]
    for chunk in chunksIndexes:
        loopOver(chunk,verbose=True)
        df = pd.DataFrame(data = commentsData, columns = ['Comment', 'Rating'])
        df.to_csv(str('./PedidosYaData'+('%d-%d.csv' % (chunk[0], chunk[-1]))), index=False, sep=';')
