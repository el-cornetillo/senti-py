import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
%pylab inline
from xml.etree import cElementTree as ET
import glob
from tqdm import tqdm
tqdm.pandas(desc="progress-bar")

pd.options.mode.chained_assignment = None

folderPath = r'C:\Users\ellio\Downloads\corpusCine\corpusCriticasCine\xmlFiles\*' ## XXX : to fill

filesPathList = list(glob.glob(folderPath))
filesPathList = [path.replace("\\", "\\\\") for path in filesPathList]
print("%d reviews in the Corpus" % len(filesPathList))

#parser = ET.XMLParser(encoding="utf-8")
#parser = ET.XMLParser(recover=True)

def cleanAscii(word):
    word = word.replace('&mdash;', '--')
    word = word.replace('&ndash;','-')
    word = word.replace('&lsquo;',"'")
    word = word.replace('&rsquo;',"'")
    word = word.replace('&ldquo;','"')
    word = word.replace('&rdquo;','"')
    word = word.replace('&', 'and')
    word = word.replace('<-','')
    word = word.replace('<P','P')
    word = word.replace('<>','')
    
    return word

def get_data(filePath):
    root = ET.fromstring(cleanAscii(open(filePath).read()))
    #root = ET.fromstring(open(filePath).read(),parser=parser)
    title = root.attrib['title']
    rank = int(root.attrib['rank'])
    summary = root.find('summary').text
    comment = root.find('body').text
    
    return title, rank, summary, comment

df = pd.DataFrame(filesPathList, columns = ['filePath'])
df['Title'], df['Rank'], df['Summary'], df['Comment'] = zip(*df['filePath'].progress_apply(lambda x : get_data(x)))

df.head()