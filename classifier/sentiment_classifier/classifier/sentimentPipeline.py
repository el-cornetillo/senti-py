from sklearn.externals import joblib
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
import numpy as np
from IPython.display import Image, display

import marisa_trie
import sys
from os import path

try:
    from nltk import word_tokenize
    l = word_tokenize('Hola como estas')
    del l
except:
    import nltk
    print('Will download some functions from the nltk package if not found on the computer')
    nltk.download('punkt')
    from nltk import word_tokenize
## DEFINE CONSTANTS

## Constants preProcessing

modules_path = sys.path
for e in modules_path:
    if path.isdir(path.join(e, 'classifier')):
        path_package = path.join(e, 'classifier')
        break

dirtyReps = re.compile(r'([^lL0])\1{1,}')
dirtySpaces = re.compile(r'(\.|,|:|;|!|\?|\[|\]|\(|\))[A-Za-z0-9]+')
dirtyK = re.compile('[^o]k')
dirtyJaja = re.compile(r'[ja]{5,}')
dirtyJeje = re.compile(r'[je]{5,}')
numbers = re.compile(r'[0-9]+')
uglySeparator = 'THIS-IS-A-SEPARATOR'
pathExpressions = path_package + '/data/expressions.txt' ## XXX : to fill
exps = set([e.split()[0] for e in open(pathExpressions, encoding='utf8').readlines()])
pathConjug = path_package + '/data/dictConjug.json' ## XXX : to fill
pathCities = path_package + '/data/Cities.txt' ## XXX : to fill
pathCountries = path_package + '/data/Countries.txt' ## XXX : to fill

with open(pathConjug, 'r') as f:
    dictConjug = json.load(f)
      ## List of special words

negWords = ['no','tampoco','ni','nunca','sin','nadie','jamas','nada','ningun','ninguno','poco']
stopNeg = [',','!','.','(',')','[',']',':',';','pero','?','con','porque','y','ninguno','ningun',
            'no','tampoco','ni','nunca','sin','nadie','jamas','nada']
ponctuation = list("[.,:;!?]()")

neutralWords = set(['mueble', 'producto','pelicula','poner','senor','venderme','negociacion','serie','pasa','paso','decir',
                'mercado_libre', 'ml','mercadolibre','productos','sistema','vendedora','vendedoras','vendedor','vendedores','ahora',
                'articulo','articulos','mensajes','tienda','mensaje','mail','mails','texto','textos','dos','tres','cuatro','cinco',
                'seis','siete','ocho','nueve','diez','once','doce','trece','catorce','quince','dieciseis','diecesiete',
                'dieciocho','diecinueve','veinte','mes','dia','dias','meses','ano','anos','cliente','persona','informacion',
                'articulo','articulos','senores','short','blusa','me','esa','el','la','los','de','por','re','a','mi','ma',
                'como','en','con','una','un','uno','y','que','su','sus','les','al','se', 'te','le','lo','ud','uds','ustedes',
                'ese','este','eso','esto','esta','estas','estos','estes','esos','esas',
               'eses','para','por','unas','unos','o', 'porque','entre', 'cuando','sobre','tambien','durante','otro',
               'otros', 'ante','antes','algunos','algunas','algun','yo','tu','cual','os','mios','mias','mio','mio',
               'tuyo','tuya','tuyos','tuyas','suyo','suya','suyos','suyas','nuetro','nuetras','nuestros','nuestras',
               'vuestro','vuestra','vuestros','vuestras','he', 'has','ha','han','hemos','habeis','haya','aqui','aqua','ahi',
               'alli','alla','k','q','qu','son','desde','es','soy','ya', 'usted','de','nos','del','son','sos','vos'])

## Constants Classifier
best_params = {'c__alpha': 0.03,
                'f__k': 200000,
                'v__max_features': 300000,
                'v__ngram_range': (1, 3)}
pathModel = path_package + '/model/sentiment_pipeline.pkl'

## Constants Prediction
decayRate = 8
GOOD_BABY = path_package + '/img/good_baby.jpg'
BAD_BABY = path_package + '/img/bad_baby.jpg'

## MARISA VECTORIZER (OPTIMIZING MEMORY OF TFIDF VECTORIZER)

class _MarisaVocabularyMixin(object):

    def fit_transform(self, raw_documents, y=None):
        super(_MarisaVocabularyMixin, self).fit_transform(raw_documents)
        self._freeze_vocabulary()
        return super(_MarisaVocabularyMixin, self).fit_transform(raw_documents, y)
        
    def _freeze_vocabulary(self):
        if not self.fixed_vocabulary_:
            self.vocabulary_ = marisa_trie.Trie(self.vocabulary_.keys())
            self.fixed_vocabulary_ = True
            del self.stop_words_
            

class MarisaCountVectorizer(_MarisaVocabularyMixin, CountVectorizer):
    pass


class MarisaTfidfVectorizer(_MarisaVocabularyMixin, TfidfVectorizer):
    def fit(self, raw_documents, y=None):
        super(MarisaTfidfVectorizer, self).fit(raw_documents)
        self._freeze_vocabulary()
        return super(MarisaTfidfVectorizer, self).fit(raw_documents, y)


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

def processDetails(word):
    word = word.replace(' re comen',' recomen')
    word = word.replace(' re ',' muy ')
    word = word.replace(' 100% ', ' muy ')
    word = word.replace('mercado libre', uglySeparator.join(['mercado','libre']))
    word = word.replace(' x ',' por ')
    word = word.replace(' q ', ' que ')
    word = word.replace(' k ', ' que ')
    return word

def processJaja(word):
    while dirtyJaja.search(word)!=None:
        word = word.replace(dirtyJaja.search(word).group(),'jaja')
    while dirtyJeje.search(word)!=None:
        word = word.replace(dirtyJeje.search(word).group(),'jaja')
    return word    

def processRep(word):
    '''la doble L atencion !!!!'''
    while dirtyReps.search(word)!=None:
        word = word.replace(dirtyReps.search(word).group(),dirtyReps.search(word).group()[0])
    return word
def processSpaces(word):
    while dirtySpaces.search(word)!=None:
        word = word.replace(dirtySpaces.search(word).group()[0],dirtySpaces.search(word).group()[0]+' ')
    return word
def processK(word):
    while dirtyK.search(word)!=None:
        word = word.replace(dirtyK.search(word).group(),dirtyK.search(word).group()[0]+'qu')
    return word
def processNumbers(word):
    while numbers.search(word)!=None:
        word = word.replace(numbers.search(word).group(),'')    
    return word
def processPoint(x):
    if len(x)==0:
        return x
    else:
        if x[-1] in stopNeg:
            return x
        else:
            return x+'.'
def processNeg(tokens):
    negIndexes = [i for i, j in enumerate(tokens) if j in negWords]
    for negWord in negIndexes:
        j=np.infty
        for f in stopNeg:
            try:
                j_ = max(tokens[(negWord+1):].index(f),0)
                j = min(j,j_)
            except:
                continue
        if j<np.infty:
            j=j+1
            for k in range(negWord+1,(min(3,int(j))+negWord)):
                if tokens[k] not in stopNeg:
                    tokens[k] = 'not_' + tokens[k]
    #return [w for w in tokens if w not in negWords]
    return tokens

def processExps(x):
    foundMatch = any(e in x.replace(' ','_') for e in exps)
    if foundMatch==False:
        return x
    else:
        x = x.replace(' ','_')
        matches = [e for e in exps if e in x]
        for e in matches:
            x = x.replace(e,uglySeparator.join(e.split('_')))
        return x.replace('_',' ')
def replaceVerbs(x):
    if len(x)==0:
        x = x
    else:
        addBack = False
        if x[-1] in ponctuation:
            endPonctu = x[-1]
            addBack = True
            x = x[:-1]
        for infinitif in dictConjug.keys():
            foundMatch = any(e in x.replace(' ','_') for e in set(dictConjug[infinitif]))
            if foundMatch==False:
                pass
            else:
                x = x.replace(' ','_')
                matches = [e for e in set(dictConjug[infinitif]) if '_'+e+'_' in x]
                for e in matches:
                    x = x.replace('_'+e+'_','_'+infinitif+'_')
                del matches
                if x.split('_')[0] in set(dictConjug[infinitif]):
                    x = '_'.join([infinitif] + x.split('_')[1:])              
                if '_'.join(x.split('_')[:2]) in set(dictConjug[infinitif]):
                    x = '_'.join([infinitif] + x.split('_')[2:])
                if x.split('_')[-1] in set(dictConjug[infinitif]):
                    x = '_'.join(x.split('_')[:-1] + [infinitif])
                if '_'.join(x.split('_')[-2:]) in set(dictConjug[infinitif]):
                    x = '_'.join(x.join('_')[:-2] + [infinitif])

                x = x.replace('_',' ')
        if addBack:
            x = x + endPonctu
        return x
def process(x):
    try:
        str(x).replace('\r','').replace('\n','')
        x = replaceAccents(x.lower())
        x = processNumbers(x)
        x = processDetails(x)
        x = processRep(x)
        x = processJaja(x)
        x = processSpaces(x)
        x = processPoint(x)
        x = processExps(x)
        x = processK(x)
        tokens = word_tokenize(replaceVerbs(x))
        tokens = [t for t in tokens if t not in neutralWords]
        tokens = processNeg(tokens)
        #tokens = [t for t in tokens if t not in uselessWords]
    except:
        tokens = ['NC']
    return ' '.join(str(re.sub('[?;,;:!"\(\)\'.]','',' '.join(tokens))).split()).replace(uglySeparator,'_')

## DEFINE UTILS FUNCTIONS BEFORE PREDICTION

def processPero(x):
            tokens = word_tokenize(x)
            if 'pero' in tokens:
                return [' '.join(tokens[:tokens.index('pero')]),' '.join(tokens[tokens.index('pero')+1:])]
            else:
                return [' '.join(tokens)]

def processMuy(x, verbose=False):
    importantWords = []
    tokens = word_tokenize(x)
    if verbose:
        print('processMuy recieves : ')
        print(tokens)
    indexOfMuy = [i for i,j in enumerate(tokens) if j =='muy']
    for k in indexOfMuy:
        try:
            importantWords.append(tokens[k+1])
        except:
            pass
    return importantWords

def predictMuy(x, sentimentPipeline, realVocab, verbose=False):
    x = ' '.join([w for w in word_tokenize(process(x)) if w.lower() in realVocab])
    score = sentimentPipeline.predict_proba([x]).squeeze()[1]
    if verbose:
        print('PredictMuy : afterProcessing : %s || Score : %.2f ' % (x,score))
    if 'muy ' in x or ' re ' in x:
        importantWords = processMuy(x,verbose)
        if verbose:
            print('Passed by muy/re condition -- Important words : %s' % str(importantWords))
        if len(importantWords)>0:
            importantScore = np.mean([sentimentPipeline.predict_proba([e]).squeeze()[1] for e in importantWords])
            if (score-0.5)*(importantScore-0.5) < 0:
                t=3
      #          while ((score + (t-1)*importanceScore)/t-0.5)*(importanceScore-0.5)<0:
      #         t = t + 1
      #          return (score+(t-1)*importantScore)/t
                while (((decayRate-t)*score + t*importantScore)/decayRate-0.5)*(importantScore-0.5)<0:
                    t = t + 1
                return ((decayRate-t)*score+(t)*importantScore)/decayRate
            else:
                return score
        else:
            return score
    else:
        return score


listCities = set([replaceAccents(e.strip().lower()) for e in open(pathCities, 'r', encoding='utf8').readlines()])
listCountries = set([replaceAccents(e.strip().lower()) for e in open(pathCountries, 'r', encoding='utf8').readlines()])

def predict(x, sentimentPipeline, realVocab, verbose=False):
    x = replaceAccents(x.lower())
    citiesRemove = [e for e in listCities if e in x]
    countriesRemove = [e for e in listCountries if e in x]
    for e in citiesRemove+countriesRemove:
        x = x.replace(e,'')
    x = processK(processExps(processSpaces(processRep(processDetails(x))))).replace(uglySeparator,'_')
    if verbose:
        print('Basics preprocessings : %s' % x)
    if len(processPero(x))>1:
        preScore,postScore = [predictMuy(e, sentimentPipeline=sentimentPipeline, realVocab=realVocab, verbose=verbose) \
                                for e in processPero(x)]
        if (preScore-0.5)*(postScore-0.5)<0:
            t=3
            #while ((preScore + (t-1)*postScore)/t-0.5)*(postScore-0.5)<0:
            #    t = t + 1
            #return (preScore + (t-1)*postScore)/t
        
            while (((decayRate-t)*preScore + t*postScore)/decayRate-0.5)*(postScore-0.5)<0:
                t = t + 1
            return ((decayRate-t)*preScore + (t)*postScore)/decayRate
        else:
            return predictMuy(x, sentimentPipeline=sentimentPipeline, realVocab=realVocab, verbose=verbose)
    else:
        return predictMuy(x, sentimentPipeline=sentimentPipeline, realVocab=realVocab, verbose=verbose)
    
def printResult(x, sentimentPipeline, realVocab, verbose=False):
    p = predict(x, sentimentPipeline=sentimentPipeline, realVocab=realVocab, verbose=verbose)
    if p>=0.5:
        display(Image(filename=GOOD_BABY, width=200, height=200))
    else:
        display(Image(filename=BAD_BABY, width=200, height=200))
    if verbose:
        print('Confidence : %.2f' % ((2*p-1)*(2*int(2*p>=1)-1)))
    return p

class SentimentClassifier:
    def __init__(self):
        self.classifier = joblib.load(pathModel)
        vocab = set(self.classifier.named_steps['v'].vocabulary_.items())
        mask = set(self.classifier.named_steps['f'].get_support(True))
        self.vocabulary = set(e[0] for e in vocab if e[1] in mask)
        del vocab
        del mask
        return
    def score(self, text, target, verbose=True):
        if verbose:
            t = time.time()
            print('Is scoring ..')
        score = self.classifier.score(text, target)
        if verbose:
            print('Scored in %d minutes' % np.rint(int(time.time()-t)/60))
            print('Score : %.5f' % score)
        return score

    def predict(self, text, verbose=False, funny=False):
        if funny:
            return printResult(text, sentimentPipeline=self.classifier, realVocab=self.vocabulary, verbose=verbose)
        else:
            return predict(text, sentimentPipeline=self.classifier, realVocab=self.vocabulary, verbose=verbose)