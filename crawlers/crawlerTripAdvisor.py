'''
	Script to extract the comments and ratings from the tripadvisor dataSet 
	downloaded here : http://times.cs.uiuc.edu/~wang296/Data/LARA/TripAdvisor/Review_Texts.zip.
	Out of interest for us, because the corpus is in english.
'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
%pylab inline
import glob
import csv

MAXSIZE = ## XXX : to fill
folderPath = r'~\trip_advisor\*' ## XXX : to fill

filesPathList = list(glob.glob(folderPath))

print('%d DAT files to proceed' % len(filesPathList))

def dat_extractor(file_path, type='list'):
    datContent = [i.strip() for i in open(file_path, encoding="utf8").readlines()]
    for line in datContent:
        if line.startswith('<Author>'):
            startIndex = datContent.index(line)
            break
    datContent = datContent[startIndex:]
    if type=='df':
        df=pd.DataFrame()
        df['comments'] = [line[9:] for line in datContent if line.startswith('<Content>')]
        df['ratings'] = [line[9:] for line in datContent if line.startswith('<Overall>')]
        return df
    else:
            return list(zip([line[9:] for line in datContent if line.startswith('<Content>')],[line[9:] for line in datContent if line.startswith('<Overall>')]))
    
s = []
for file in filesPathList:
    s = s + dat_extractor(file.replace("\\", "\\\\"))
    
s_short = s[:MAXSIZE]

df = pd.DataFrame(np.asarray(s_short), columns = ['comment', 'rating'])


