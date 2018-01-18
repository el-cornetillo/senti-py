import re
import json

## Constants importation Data
""" pathsData = { 'SENSACINE_SERIES' : "Classifier/data/sensaCineSerie.txt",
              'SENSACINE_MOVIES' : "Classifier/data/sensaCineMovie.txt",
              'PEDIDOS_YA' : "Classifier/data/pedidosYa.txt",
              'TRIP_ADVISOR_HOTEL' : "Classifier/data/tripAdvisorHotel.txt",
              'TRIP_ADVISOR_RESTAURANT' : "Classifier/data/tripAdvisorRestaurant.txt",
              'TRIP_ADVISOR_ATTRACTION' : "Classifier/data/tripAdvisorAttraction.txt",
              'OPEN_CINE' : "Classifier/data/openCine.txt",
              'QUEJAS_ONLINE' : "Classifier/data/quejas.txt",
              'APESTAN' : "Classifier/data/apestan.txt",
              'BAD_TWEETS' : "Classifier/data/badTweets.txt",
              'GOOD_TWEETS' : "Classifier/data/goodTweets.txt",
              'TASS_DATASET' : "Classifier/data/tassTweets.txt",
              'MERCADOLIBRE_POS' : "Classifier/data/MercadoPos.txt",
              'MERCADOLIBRE_NEG' : "Classifier/data/MercadoNeg.txt" } """

MERCADO_RATIO = 50000
dataDelimiter = '__dataDelimiter__'

## Constants preProcessing
path = './'
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
best_params = {'f__k': 70000, 'v__max_features': 200000, 'v__ngram_range': (1, 4), 'c__alpha': 0.01}
pathModel = path_package + '/model/sentiment_pipeline.pkl'

## Constants Prediction
decayRate = 8

GOOD_BABY = path_package + '/img/good_baby.jpg'
BAD_BABY = path_package + '/img/bad_baby.jpg'
