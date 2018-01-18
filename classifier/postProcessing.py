from .constants import *
import spacy
import es_core_web_md
nlp = es_core_web_md.load()
from nltk import word_tokenize

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







