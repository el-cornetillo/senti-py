import re
import bs4 ## BeautifulSoup4, for html extraction
import urllib.request
import pandas as pd
import numpy as np
import re ## for reg ex

from pymongo import MongoClient
mongoClient = MongoClient('mongodb://localhost:27017/')

with open('quejasUrls.json') as f:
    urls = f.read()
    
quejasUrls = re.findall('{[^{]*}',urls)
quejasUrls = [re.findall('"[^\s]*"',e)[1].replace('"','') for e in quejasUrls]

lastindex= len(quejasUrls)

def loop(ind):
    try:
        for queja in reversed(quejasUrls[:ind]):
            htmlContent = urllib.request.urlopen(queja).read()
            soup = bs4.BeautifulSoup(htmlContent, 'html5lib')
            comment = soup.find('span', attrs={'class': 'texto_queja_comun'}).text.replace('\n',' ')
            mongoClient['webScraper']['Quejas'].insert_one({'comment': comment})
            global lastindex
            lastindex=lastindex-1
            print(queja)
            print(lastindex)
    except:
        print('restarted')
        loop(lastindex)