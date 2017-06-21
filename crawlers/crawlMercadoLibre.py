''' Crawls comments from MercadoLibre.com'''

import bs4 ## BeautifulSoup4, for html extraction
import urllib.request
import pandas as pd
import numpy as np
import re ## for reg ex

baseUrl = 'http://www.mercadolibre.com.ar/jm/profile?id='
M = pow(10,10)
alreadySearched = []
numbers = re.compile(r'[0-9]+')
perPages = 25

#from pymongo import MongoClient
#mongoClient = MongoClient('mongodb://localhost:27017/')
#import hashlib

#def md5(inputStr):
#    return hashlib.md5(inputStr.encode('utf-8')).hexdigest()

def crawlMercado():
	''''
		Crawls comments through mercadoLibre.com and writes them into mercadoPos.txt and mercadoNeg.txt
	'''
    for numId in range(M):
        if numId not in alreadySearched:
            try:
                urllib.request.urlopen('https://www.google.com.ar/') ## Verify that the internet connection is OK
                try:
                	## try-catch block to verify the current page is available
                    htmlContent = urllib.request.urlopen(baseUrl + str(numId)).read()
                    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
                    if soup.find('h1', {'class': 'ml-title'}).text=='Reputación':
                        commentsCategory = [(e['href'],numbers.search(e.text).group()) for e in \
                                            soup.find('nav', {'class': ' reputation-filters'}).findAll('a')[1:]]
                        for t in commentsCategory:
                            if 'negative' in t[0]:
                                numberPages = int(t[1])//perPages + 1
                                for k in range(numberPages):
                                    try:
                                        htmlContent = urllib.request.urlopen(t[0].replace('offset=0','offset='+str(k*25))).read()
                                        print('Could connect %d-%d NEGATIVE' % (numId,k))
                                        soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
                                        L = [re.search(r'\".*\"',e.find('label', {'class': 'feedback-trigger'}).text.replace('\n','').replace('\t','')).group()[1:-1] for e \
                                               in soup.findAll('article', {'class': 'feedback-box feedback-negative'})]
                                        with open('MercadoNeg.txt', 'a', encoding='utf8') as f:
                                            for e in L:
                                                f.write(e)
                                                f.write("\n")
                                        print('-----------------------------------------------------------------------------Added %d negative comments' % len(L))
                                        #mongoClient['webScraper']['MercadoLibre'].insert_many(list(map(lambda t: {"_id": md5(t), "comment": t, 'rating': 0}, L)), ordered=False)
                                        del L
                                    except:
                                        print('Problem with %d-%d NEGATIVE' % (numId,k))
                                        pass
                            if 'positive' in t[0]:
                                numberPages = int(t[1])//perPages + 1
                                for k in range(numberPages):
                                    try:
                                        htmlContent = urllib.request.urlopen(t[0].replace('offset=0','offset='+str(k*25))).read()
                                        print('Could connect %d-%d POSITIVE' % (numId,k))
                                        soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
                                        L = [re.search(r'\".*\"',e.find('label', {'class': 'feedback-trigger'}).text.replace('\n','').replace('\t','')).group()[1:-1] for e \
                                               in soup.findAll('article', {'class': 'feedback-box feedback-positive'})]
                                        with open('MercadoPos.txt', 'a', encoding='utf8') as f:
                                            for e in L:
                                                f.write(e)
                                                f.write('\n')
                                        print('-----------------------------------------------------------------------------Added %d positive Comments' % len(L))
                                        #mongoClient['webScraper']['MercadoLibre'].insert_many(list(map(lambda t: {"_id": md5(t), "comment": t, 'rating': 1}, L)), ordered=False)
                                        del L
                                    except:
                                        print('Problem with %d-%d POSITIVE' % (numId,k))
                                        pass
                    global alreadySearched
                    alreadySearched.append(numId)
                except:
                	##If the current page is not a valid page continue the loop over numId
                    print('couldnt %d' % numId)
                    global alreadySearched
                    alreadySearched.append(numId)
                    pass
            except:
            	## If there is a connection problem automaticly restarts (recursive call to crawlMercado() until it connects)
                print('stopped at %d because of a connection problem' % numId)
                print('Will restart')
                crawlMercado()
    

crawlMercado()