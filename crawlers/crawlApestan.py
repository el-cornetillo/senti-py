import bs4 ## BeautifulSoup4, for html extraction
from urllib.request import Request, urlopen
import pandas as pd
import numpy as np
import re ## for reg ex

from pymongo import MongoClient
mongoClient = MongoClient('mongodb://localhost:27017/')

htmlUrl = 'https://www.apestan.com/countries'

req = Request(htmlUrl, headers={'User-Agent': 'Mozilla/5.0'})
htmlContent = urlopen(req).read()
soup = bs4.BeautifulSoup(htmlContent, 'html5lib')

utilsDict = {re.search('[0-9]+',e.find('a')['href']).group(): e.find('span').text for e in soup.findAll('p', {'class': 'bold'})}
idCountries = {re.search('[0-9]+',e.find('a')['href']).group(): e.find('a').text for e in soup.findAll('p', {'class': 'bold'})}
alreadyDone = []
alreadyDoneUrl = []
countryVisited = []
def crawlCountry(idCountry,numberComments):
    urlQuejas = []
    for k in range(max(1,(int(numberComments)//30))):
        if k not in alreadyDone:
            htmlUrl = "https://www.apestan.com/countries/pagenumber_" +str(k+1)+"/countryid_" + str(idCountry) + "/isapproved_yes/deleted_0"
            req = Request(htmlUrl, headers={'User-Agent': 'Mozilla/5.0'})
            htmlContent = urlopen(req).read()
            soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
            urlQuejas = [e.find('a')['href'] for e in soup.findAll('div', {'class': 'heading-4'})[1:]]
            print('Did %d of %d pages of country %s' % ((k+1),max(1,(int(numberComments)//30)), idCountries[idCountry]))
            for url in urlQuejas:
                if url not in alreadyDoneUrl:
                    req = Request('https://www.apestan.com'+url, headers={'User-Agent': 'Mozilla/5.0'})
                    htmlContent = urlopen(req).read()
                    soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
                    comment = ' '.join([e.text for e in soup.find('div', {'class': 'text-block'}).findAll('span')]).replace('\n',' ')
                    mongoClient['webScraper']['Apostan'].insert_one({'comment': comment})
                    global alreadyDoneUrl
                    alreadyDoneUrl.append(url)
                    print('inserted')
            global alreadyDone
            alreadyDone.append(k)
            global alreadyDoneUrl
            alreadyDoneUrl = []
              
def crawlIt():
    try:
        for (k,v) in utilsDict.items():
            if idCountries[k] not in countryVisited:
                print('Doing country : ' + idCountries[k])
                crawlCountry(k,v)
                global countryVisited
                countryVisited.append(idCountries[k])
    except:
        print('restarted')
        crawlIt()