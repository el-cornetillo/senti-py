
## IMPORT PACKAGES

print('Loading data manipulation libraries ..')
import pandas as pd
import numpy as np
from tqdm import tqdm
tqdm.pandas(desc="progress-bar")
pd.options.mode.chained_assignment = None

print('Loading python standard libraries ..')
import re
import json
import time
from nltk import word_tokenize

print('Loading scikit learn libraries ..')
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib

print('Loading the project modules ..')
import marisa_trie

## DEFINE CONSTANTS

pathsData = { 'SENSACINE_SERIES' : "Classifier/dataset/sensaCineSerie.txt",
              'SENSACINE_MOVIES' : "Classifier/dataset/sensaCineMovie.txt",
              'PEDIDOS_YA' : "Classifier/dataset/pedidosYa.txt",
              'TRIP_ADVISOR_HOTEL' : "Classifier/dataset/tripAdvisorHotel.txt",
              'TRIP_ADVISOR_RESTAURANT' : "Classifier/dataset/tripAdvisorRestaurant.txt",
              'TRIP_ADVISOR_ATTRACTION' : "Classifier/dataset/tripAdvisorAttraction.txt",
              'OPEN_CINE' : "Classifier/dataset/openCine.txt",
              'QUEJAS_ONLINE' : "Classifier/dataset/quejas.txt",
              'APESTAN' : "Classifier/dataset/apestan.txt",
              'BAD_TWEETS' : "Classifier/dataset/badTweets.txt",
              'GOOD_TWEETS' : "Classifier/dataset/goodTweets.txt",
              'TASS_DATASET' : "Classifier/dataset/tassTweets.txt",
              'MERCADOLIBRE_POS' : "Classifier/dataset/MercadoPos.txt",
              'MERCADOLIBRE_NEG' : "Classifier/dataset/MercadoNeg.txt" }

MERCADO_RATIO = 100000
dataDelimiter = '__dataDelimiter__'

## Constants preProcessing

dirtyReps = re.compile(r'([^lL0])\1{1,}')
dirtySpaces = re.compile(r'(\.|,|:|;|!|\?|\[|\]|\(|\))[A-Za-z0-9]+')
dirtyK = re.compile('[^o]k')
dirtyJaja = re.compile(r'[ja]{5,}')
dirtyJeje = re.compile(r'[je]{5,}')
numbers = re.compile(r'[0-9]+')
uglySeparator = 'THIS-IS-A-SEPARATOR'
pathExpressions = 'Classifier/dataset/expressions.txt' ## XXX : to fill
exps = set([e.split()[0] for e in open(pathExpressions, encoding='utf8').readlines()])
pathConjug = "Classifier/dataset/dictConjug.json" ## XXX : to fill

with open(pathConjug, 'r') as f:
    dictConjug = json.load(f)

      ## List of special words

negWords = ['no','tampoco','ni','nunca','sin','nadie','jamas','nada','ningun','ninguno','poco']
stopNeg = [',','!','.','(',')','[',']',':',';','pero','?','con','porque','y','ninguno','ningun',
            'no','tampoco','ni','nunca','sin','nadie','jamas','nada']
ponctuation = list("[.,:;!?]()")

neutralWords = set(['mueble', 'producto','pelicula','poner','senor','venderme','negociacion','serie','pasa','paso','decir',
                'mercado_libre', 'ml','mercadolibre','productos','sistema','vendedora','vendedoras','vendedor','vendedores','ahora',
                'articulo','articulos','mensajes','mensaje','mail','mails','texto','textos','dos','tres','cuatro','cinco',
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
pathModel = 'sentiment_pipeline.pkl'

## Constants Prediction
decayRate = 8
GOOD_BABY = 'Classifier/img/good_baby.jpg'
BAD_BABY = 'Classifier/img/bad_baby.jpg'

## GET DATA FUNCTION

def ingest(path=None, save=False, verbose=True):
    if save and path is None:
        print('If save is True, you must specify an explicit path')
        return 
    else:
        if verbose:
            print('Loading data ..')
            print(' ')
        text = []
        target = []
        nComments = 0
        for path in pathsData.items():
            if path[0] not in ['MERCADOLIBRE_POS', 'MERCADOLIBRE_NEG']:
                data = [e.split(dataDelimiter) for e in open(path[1], encoding='utf8').readlines()]
                text += [e[0] for e in data if len(e)==2]
                target += [float(e[1].strip()) for e in data if len(e)==2]
                del data
                if verbose:
                    print('%s : %d' % (path[0], len(text) - nComments))
                nComments = len(text)

        #text += list(set([e.strip() for e in open(pathsData['MERCADOLIBRE_POS'], encoding='utf8').readlines()]))[:MERCADO_RATIO]
        text += list(set([e.strip() for e in open(pathsData['MERCADOLIBRE_POS'], encoding='utf8').readlines()]))[:int((MERCADO_RATIO/2))] \
        + list(set(['no ' + e.strip() for e in open(pathsData['MERCADOLIBRE_NEG'], encoding='utf8').readlines() if \
        len(e.split())<=4 and len(e.split())>0 and e.split()[0].lower() not in negWords]))[:int((MERCADO_RATIO)/2)]
        target += [5] * (len(text) - nComments)
        if verbose:
            print('%s : %d' % ('MERCADOLIBRE_GOOD', len(text) - nComments))
        nComments = len(text)

        text += [e.strip() for e in open(pathsData['MERCADOLIBRE_NEG'], encoding='utf8').readlines()] \
        + list(set(['no ' + e.strip() for e in open(pathsData['MERCADOLIBRE_POS'], encoding='utf8').readlines() if \
        len(e.split())<=4 and len(e.split())>0 and e.split()[0].lower() not in negWords]))[:MERCADO_RATIO]
        target += [0] * (len(text) - nComments)
        if verbose:
            print('%s : %d' % ('MERCADOLIBRE_BAD', len(text) - nComments))
        nComments = len(text)

        if verbose:
            print(' ')
            print('TOTAL : %d' % nComments)
        if save:
            with open(path, 'a', encoding='utf8'):
                for ix,e in enumerate(text):
                    f.write(' '.join([str(e), dataDelimiter, str(target(ix))]))
                    f.write('\n')
        return text, target

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

## PROCESSOR CLASS TO PROCESS DATA BEFORE LEARNING

class Processor:
    def __init__(self, neutralWords=neutralWords, verbose=False, save=False, path=None):
        if save and path is None:
            print('If save is True, you must specify an explicit path')
            return
        else:
            self.verbose = verbose
            self.neutralWords = neutralWords
            self.save = save
            self.path = path
            return

    def binarize(self,r):
        if r>=4:
            return 1
        elif r<=2.5:
            return 0
        else:
            return np.nan

    def processDocs(self, text, target):
        df = pd.DataFrame(data = list(zip(text, target)), columns = ['comment','rating'])
        df = df.sample(frac=1).reset_index(drop=True)
        if self.verbose:
            print('Number of comments before binarize : %d' % df.shape[0])
        df['target'] = df['rating'].apply(lambda x : self.binarize(x))
        df.dropna(how='any', inplace=True)
        if self.verbose:
            print('Number of comments after binarize : %d' % df.shape[0])
        text = [process(e) for e in tqdm(df['comment'])]
        target = list(df['target'])
        df = pd.DataFrame(list(zip(text,target)), columns = ['comment', 'target'])
        del text
        del target
        df = df[df['comment']!='NC']
        if self.verbose:
            print('Number of comments after preprocessing : %d' % df.shape[0])
        text = list(df['comment'])
        target = list(df['target'])
        del df
        if self.save:
            with open(self.path, 'a', encoding='utf8') as f:
                for ix,e in enumerate(text):
                    f.write(' '.join([str(e),dataDelimiter,str(target[ix])]))
                    f.write('\n')

        return text, target

## DEFINE UTILS FUNCTIONS

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
    #word = word.replace('1000',uglySeparator+'mil')
    #word = word.replace('100',uglySeparator+'cien')
    #word = word.replace('10',uglySeparator+'diez')
    while numbers.search(word)!=None:
        word = word.replace(numbers.search(word).group(),'')
    #word = word.replace(uglySeparator+'mil','1000')
    #word = word.replace(uglySeparator+'cien','100')
    #word = word.replace(uglySeparator+'diez','10')    
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
                    x = x.replace(x.split('_')[0]+'_'+x.split('_')[1]+'_'+x.split('_')[2],infinitif+'_'+x.split('_')[1]+'_'+x.split('_')[2])
                if '_'.join(x.split('_')[:2]) in set(dictConjug[infinitif]):
                    x = x.replace('_'.join(x.split('_')[:2])+'_'+x.split('_')[2]+'_'+x.split('_')[3],infinitif+'_'+x.split('_')[2]+'_'+x.split('_')[3])
                if x.split('_')[-1] in set(dictConjug[infinitif]):
                    x = x.replace(x.split('_')[-3]+'_'+x.split('_')[-2]+'_'+x.split('_')[-1],x.split('_')[-3]+'_'+x.split('_')[-2]+'_'+infinitif)
                if '_'.join(x.split('_')[-2:]) in set(dictConjug[infinitif]):
                    x = x.replace(x.split('_')[-4]+'_'+x.split('_')[-3]+'_'+'_'.join(x.split('_')[-2:]),x.split('_')[-4]+'_'+x.split('_')[-3]+'_'+infinitif)

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
            if 'ADJ' in [nlp(tokens[k+1])[0].pos_,nlp(tokens[k+1]+'s')[0].pos_]:
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
                while ((score + t*importantScore)/decayRate-0.5)*(importantScore-0.5)<0:
                    t = t + 1
                return (score+(t+1)*importantScore)/decayRate
            else:
                return score
        else:
            return score
    else:
        return score

def predict(x, sentimentPipeline, realVocab, verbose=False):
    x = processK(processExps(processSpaces(processRep(processDetails(replaceAccents(x.lower())))))).replace(uglySeparator,'_')
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
        
            while ((preScore + t*postScore)/decayRate-0.5)*(postScore-0.5)<0:
                t = t + 1
            return (preScore + (t+1)*postScore)/decayRate
        else:
            return predictMuy(x, sentimentPipeline=sentimentPipeline, realVocab=realVocab, verbose=verbose)
    else:
        return predictMuy(x, sentimentPipeline=sentimentPipeline, realVocab=realVocab, verbose=verbose)
    
def printResult(x, sentimentPipeline, realVocab, verbose=False):
    p = predict(x)
    if p>=0.5:
        display(Image(filename=GOOD_BABY, width=200, height=200))
    else:
        display(Image(filename=BAD_BABY, width=200, height=200))
    if verbose:
        print('Confidence : %.2f' % ((2*p-1)*(2*int(2*p>=1)-1)))
    return p

## CLASS TO IMPLEMENT THE CLASSIFIER

class sentimentClassifier:
    def __init__(self, ngram_range = best_params['v__ngram_range'], max_features = best_params['v__max_features'],
                        k = best_params['f__k'], alpha = best_params['c__alpha'], lightModel = False):
        self.lightModel = lightModel
        if self.lightModel:
            self.sentiment_pipeline = Pipeline((
            ('v', MarisaTfidfVectorizer.MarisaTfidfVectorizer(TfidfVectorizer(ngram_range=ngram_range, \
                                                                         max_features=max_features))),
            ('f', SelectKBest(chi2, k=k)),
            ('c', MultinomialNB(alpha=alpha))
            ))
        else:
            self.sentiment_pipeline = Pipeline((
            ('v', TfidfVectorizer(ngram_range=ngram_range, max_features=max_features)),
            ('f', SelectKBest(chi2, k=k)),
            ('c', MultinomialNB(alpha=alpha))
            ))
        self.vocabulary = None
        return
    def fit(self, text, target, verbose=True):
        if verbose:
            print('Proportion of good comments : %f || bad comments : %f' % (np.mean(target), 1-np.mean(target)))
            t = time.time()
            print(' ')
            print('Is fitting ..')
        self.sentiment_pipeline.fit(text, target)
        if verbose:
            print('Fitted in %d minutes' % np.rint(int(time.time()-t)/60))
            print(' ')
            print('Storing the vocabulary ..')
        vocab = set(self.sentiment_pipeline.named_steps['v'].vocabulary_.items())
        mask = set(self.sentiment_pipeline.named_steps['f'].get_support(True))
        self.vocabulary = set(e[0] for e in vocab if e[1] in mask)
        del vocab
        del mask
        #self.vocabulary = set([e[0] for e in self.sentiment_pipeline.named_steps['v'].vocabulary_.items() if e[1] in set(self.sentiment_pipeline.named_steps['f'].get_support(True))])
        if verbose:
            print('Vocabulary stored')
            print('')
            print('DONE')

    def score(self, text, target, verbose=True):
        if verbose:
            t = time.time()
            print('Is scoring ..')
        score = self.sentiment_pipeline.score(text, target)
        if verbose:
            print('Scored in %d minutes' % np.rint(int(time.time()-t)/60))
            print('Score : %.5f' % score)
        return score

    def predict(self, text, verbose=False, funny=False):
        if funny:
            return printResult(text, sentimentPipeline=self.sentiment_pipeline, realVocab=self.vocabulary, verbose=verbose)
        else:
            return predict(text, sentimentPipeline=self.sentiment_pipeline, realVocab=self.vocabulary, verbose=verbose)

    def save(self, path = pathModel):
        joblib.dump(self.sentiment_pipeline, path)

## LOADING 
print('Loading Spacy library ..')
import spacy
import es_core_web_md
nlp = es_core_web_md.load()