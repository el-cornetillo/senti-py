from nltk import word_tokenize
from nltk.stem import SnowballStemmer
stemmer = SnowballStemmer('spanish')
import re 

pathGood = 'goodLexStem.txt'
pathBad = 'badLexStem.txt'

goodLexStem = [e.strip() for e in open(pathGood).readlines()]
badLexStem = [e.strip() for e in open(pathBad).readlines()]

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

    
uselessWords = ['me','esa','el','la','los','de','por','re','a','mi','ma','como','en','con','una','un','uno','y','que','su'
               'sus','les','al','se', 'te','lo','ese','este','eso','esto','esta','estas','estos','estes','esos','esas',
               'eses','para','por','sin','unas','unos','o', 'porque','entre', 'cuando','sobre','tambien','durante','otro',
               'otros', 'ante','antes','algunos','algunas','algun','yo','tu','cual','os','mios','mias','mio','mio',
               'tuyo','tuya','tuyos','tuyas','suyo','suya','suyos','suyas','nuetro','nuetras','nuestros','nuestras',
               'vuestro','vuestra','vuestros','vuestras','he', 'has','ha','han','hemos','habeis','haya','aqui','aqua','ahi',
               'alli','alla','k','q','son','desde','pasa','paso','decir']


dirtyReps = re.compile(r'(.)\1{1,}')
dirtySpaces = re.compile(r'(\.|,|:|;|!|\?|\[|\]|\(|\))[A-Za-z0-9]+')

def processSpaces(word):
    while dirtySpaces.search(word)!=None:
        word = word.replace(dirtySpaces.search(word).group()[0],dirtySpaces.search(word).group()[0]+' ')
    return word

def processRep(word):
    while dirtyReps.search(word)!=None:
        word = word.replace(dirtyReps.search(word).group(),dirtyReps.search(word).group()[0])
    return word

def LexClassNeg(word,verbose=False, mode="score"):
    words = [replaceAccents(w.lower()) for w in word_tokenize(word) if w.lower() not in uselessWords]
    badWords = []
    goodWords = []
    for w in set(words):
        indexOfOccurences = [i for i, j in enumerate(words) if j == w]
        for z in indexOfOccurences:
            if stemmer.stem(w) in goodLexStem:
                found=False
                k=0
                while found==False and k<=4:
                    k=k+1
                    if k==1:
                        found = ' '.join(words[z-k:z]) in ['no','nunca','ni','tampoco','nada']
                    else:
                        found = (re.search(' no | nunca | ni | tampoco | nada ',' '.join([""]+words[z-k:z]))!=None)
                if found==False:
                    goodWords.append(w)
                else:
                    found=None
                    i=0
                    while found==None and i<=k-1:
                        i=i+1
                        found = re.search('\.|,|:|;|!|\?|\[|\]|\(|\)',' '.join(words[z-i:z]))
                    if found==None:
                        badWords.append(w)
                    else:
                        goodWords.append(w)
            if stemmer.stem(w) in badLexStem:
                found=False
                k=0
                while found==False and k<=4:
                    k=k+1
                    if k==1:
                        found = ' '.join(words[z-k:z]) in ['no','nunca','ni','tampoco','nada']
                    else:
                        found = (re.search(' no | nunca | ni | tampoco | nada ',' '.join([""]+words[z-k:z]))!=None)
                if found==False:
                    badWords.append(w)
                else:
                    found=None
                    i=0
                    while found==None and i<=k-1:
                        i=i+1
                        found = re.search('\.|,|:|;|!|\?|\[|\]|\(|\)',' '.join(words[z-i:z]))
                    if found==None:
                        goodWords.append(w)
                    else:
                        badWords.append(w)
                    

    if verbose:    
        print('Count of good words : %d' % len(goodWords))
        print(goodWords)
        print('')
        print('Count of bad words : %d' % len(badWords))
        print(badWords)

    if mode =="score":
        try:
            scoreLex = (len(goodWords))/(len(goodWords)+len(badWords))
        except:
            scoreLex = 1
        return scoreLex
    else:
        return len(goodWords), len(badWords)


toClassify = "Hermosa pelicula, la verdad que no puede abburir por lo tan bueno que es." ## XXX : to fill
LexClassNeg(toClassify)