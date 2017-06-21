from pattern.web import Twitter
from unidecode import unidecode
from nltk.tokenize import TweetTokenizer # a tweet tokenizer from nltk.
import numpy as np
import time
tokenizer = TweetTokenizer()
t = Twitter()
badWords = ['chantas','insoportable','orto','traidor','traidores','garca','garcas','impostor','impostores','frio',
            'malisimo','malisima','malisimas','malisimos','odio','odios','mentiroso','mentirosos','mentirosa','mentirosas',
            'pelotudeces','chorro','chorros','ladrones','ladron','boludos','catastrofe','bajon','ratas de mierda',
            'rata de mierda', 'forro', 'forra','malparido','malparidos','decepcion','decepcionado','decepcionada','hdp',
            'choteada','choteadas','ni en pedo','ni borracho','dejen de joder','jodete','me estan jodiendo','me estas jodiendo',
            'me estas cagando','me estan cagando','basura','cagadas','harto de','chupar la pija','pito','choteada', 'no me gusto',
            'muy malo','muy mala', 'muy malas', 'muy malos','mande a la mierda','mandan a la mierda','verga','rompe el culo',
            'chupaculo', "chupaculos",'harto de','no doy mas','hinchar las pelotas','me cago en la concha de tu madre','cagada',
            'hincha las pelotas','chupenmela','la puto que te re contra pario', 'andate a la re concha de la lora', 'andate a la mierda',
            'hijueputa', 'rompe las bolas','gil','giles','nazi del orto','forro','forra', 'me saca', 'en la loma del culo',
            'en la loma del orto','cagada','me cago','peligroso','peligrosa','peligrosos','peligrosas','triste','tristeza','tristes', 'peina','lastima','lastimado','lastimada','lastimados','lastimadas' 'malicima',
            'tarde frio','demorar','arrepiento','arrepintio','decepcionados','decepcionado','negativos','demoro','tontos',
            'tontas','tonta','tonto','carajo','desinteres','inrecomendable','desaparecio','costosos','costoso','romper la pelota',
            'dificiles','dificil', 'complicado','complicadisimo ','pesadisimo','pesado','pesados',
            'precios caros','precio caro','ni empedo','lamentablemente','rabia','lastima','lamento','imposible',
            'asquerosas','asquerosos','asqueroso','bronca','verguenza','inmaduros','inmadurez','ridiculos','aguantate boludo',
            'insoportables','anden a la mierda','rompe el orto','chupame la pija','chupaculo',
            'chupame el pito','no es muy bueno', 'no me gusto', 'imbancable', 'chupamedias', 'zarpado','por el orto',
            'toqueton', 'zarpados', 'conchudo', 'conchuda','conchudos', 'conchudas','mala leche', 'ortiba', 'me cago en la conche de tu hermana',
            'forro', 'forra','yearsa','tarado','tarados','chulengo','chulengos','berreta','ratas de mierda','rata de mierda','cacuija',
            'buitre','cacuijas','buitres','mamerto','marmetos','guacala','cagador','pastrulo','verreta','puteadas','torpe','me canse de',
            'callate','al pedo','baboso','la concha de tu madre','la puta que ta pario', 'la re concha','putos','puto','puta','putas',
            'hijos de las mil putas','la concha de la lora','mucho que mejorar','solo te puede entrener si', 'chupenla', 'chupala','ni borraho',
            'cagon', 'marica','a la mierda' 'maricones', 'maricon', 'cagones', 'cheto', 'cheta', 'chetos', 'chetas', 'boludeando','boludear',
            'hijo de puta','pelotudo','chorro','sos una mierda','boludo del orto', 'zorra','gil','pelotudos','boludos','gilipolla']

goodWords = ['preciosas','satisfacion','viva amor','amar','vamooooss','amarlos','amarlas','querelas','quererlos','vamooss','amor','precioso','piolas','preciosa',
             'preciosos','preciosas','satisfacion','viva amor','enamorado','enamorada',
            'enamorados','enamoradas','agradecidas','agradecidos','agradecido','agradecida','cumplidora','honesta','felices','satisfecho',
             'satisfechos','contentos','contento','recomendable','espectacular','piola','buenos','buenas','buenisimo',
             'buenisima','buenisimos','amo']

dataDelimiter = '__dataDelimiter__'

class TweetCrawler:
      def __init__(self, mode, badWords = badWords, goodWords = goodWords):
            self.mode = mode
            self.badWords = badWords
            self.goodWords = goodWords
            self.searchedGood = []
            self.searchedBad = []
            return
      def tokenizeTweet(self,tweet):
            try:
                  tweet = tweet.lower()
                  tokens = tokenizer.tokenize(tweet)
                  tokens = filter(lambda t: not t.startswith('@'), tokens)
                  tokens = filter(lambda t: not t.startswith('#'), tokens)
                  tokens = filter(lambda t: not t.startswith('http'), tokens)
                  tokens = filter(lambda t: not t.startswith('rt'), tokens)
                  return ' '.join(list(tokens))
            except:
                  return np.nan
      def crawl(self, verbose=True):
            if self.mode=='good':
                  i = None
                  goodTweets = []
                  try:
                        for w in self.goodWords:
                            if w not in self.searchedGood:
                                  for j in range(10):
                                        for tweet in t.search(w, start=i, count=50):
                                            goodTweets.append(self.tokenizeTweet(tweet.text))
                                            i = tweet.id
                            self.searchedGood.append(w)
                  except:
                        goodTweets = list(set(goodTweets))
                        goodTweets = [unidecode(w) for w in goodTweets]
                        goodtweets = [self.tokenizeTweet(w) for w in goodTweets]
                        goodTweets = [str(w) for w in goodTweets if str(w) != 'nan']
                        with open(r'C:\Users\ellio\Documents\Stage Sondeos\Sentiment Analysis\Classifier\dataset\goodTweet_.txt', 'a') as f:
                              for tweet in goodTweets:
                                    f.write(tweet + ' ' + dataDelimiter + ' ' + '5')
                                    f.write('\n')
                        if verbose:
                              print('Added %d positive tweets' % len(goodTweets))
                        self.mode = 'bad'
                        if verbose:
                            print('Sleeping ..')
                        time.sleep(700)
                        if verbose:
                            print('Got back to Crawl')
                        self.crawl(verbose=verbose)
            if self.mode=='bad':
                  i = None
                  badTweets = []
                  try:
                        for w in self.badWords:
                            if w not in self.searchedBad:                            
                                for j in range(10):
                                    for tweet in t.search(w, start=i, count=50):
                                        badTweets.append(self.tokenizeTweet(tweet.text))
                                        i = tweet.id
                            self.searchedBad.append(w)
                  except:
                        badTweets =list(set(badTweets))
                        badTweets = [unidecode(w) for w in badTweets]
                        badtweets = [self.tokenizeTweet(w) for w in badTweets]
                        badTweets = [str(w) for w in badTweets if str(w) != 'nan']
                        with open(r'C:\Users\ellio\Documents\Stage Sondeos\Sentiment Analysis\Classifier\dataset\badTweets_.txt', 'a') as f:
                              for tweet in badTweets:
                                    f.write(tweet + ' ' + dataDelimiter + ' ' + '0')
                                    f.write('\n')
                        if verbose:
                              print('Added %d negative tweets' % len(badTweets))
                        self.mode = 'good'
                        if verbose:
                            print('Sleeping ..')
                        time.sleep(700)
                        if verbose:
                            print('Got back to Crawl')
                        self.crawl(verbose=verbose)
      def addWord(self, word):
            if self.mode == 'good':
                  self.goodWords.append(word)
            else:
                  self.badWords.append(word)
            return