import re
import json

## Constants Twitter crawler

badwords = ['peligroso','peligrosa','peligrosos','peligrosas','triste','tristeza','tristes', 'peina','lastima','lastimado','lastimada','lastimados','lastimadas' 'malicima',
            'tarde frio','demorar','arrepiento','arrepintio','decepcionados','decepcionado','negativos','demoro','tontos',
            'tontas','tonta','tonto','carajo','desinteres','inrecomendable','desaparecio','costosos','costoso','romper la pelota',
            'dificiles','dificil', 'complicado','complicadisimo ','pesadisimo','pesado','pesados',
            'precios caros','precio caro','ni empedo','lamentablemente','rabia','lastima','lamento','imposible',
            'asquerosas','asquerosos','asqueroso','bronca','verguenza','inmaduros','inmadurez','ridiculos','aguantate boludo',
            'insoportables','insoportable','orto','traidor','traidores','garca','garcas','impostor','impostores','frio',
            'malisimo','malisima','malisimas','malisimos','odio','odios','mentiroso','mentirosos','mentirosa','mentirosas',
            'pelotudeces','chorro','chorros','ladrones','ladron','boludos','catastrofe','bajon','ratas de mierda',
            'rata de mierda', 'forro', 'forra','malparido','malparidos','decepcion','decepcionado','decepcionada','hdp',
            'choteada','choteadas','ni en pedo','ni borracho','dejen de joder','jodete','me estan jodiendo','me estas jodiendo',
            'me estas cagando','me estan cagando','basura','cagadas','harto de','chupar la pija','pito','choteada', 'no me gusto',
            'muy malo','muy mala', 'muy malas', 'muy malos','mande a la mierda','mandan a la mierda','verga','rompe el culo',
            'chupaculo', "chupaculos",'harto de','no doy mas','hinchar las pelotas','me cago en la concha de tu madre','cagada',
            'hincha las pelotas','chupenmela','la puto que te re contra pario', 'andate a la re concha de la lora', 'andate a la mierda',
            'hijueputa', 'rompe las bolas','gil','giles','nazi del orto','forro','forra', 'me saca', 'en la loma del culo',
            'en la loma del orto','cagada','me cago','anden a la mierda','rompe el orto','chupame la pija','chupaculo',
            'chupame el pito','no es muy bueno', 'no me gusto', 'imbancable', 'chupamedias', 'zarpado','por el orto',
            'toqueton', 'zarpados', 'conchudo', 'conchuda','conchudos', 'conchudas','mala leche', 'ortiba', 'me cago en la conche de tu hermana',
            'forro', 'forra','yearsa','tarado','tarados','chulengo','chulengos','berreta','ratas de mierda','rata de mierda','cacuija',
            'buitre','cacuijas','buitres','mamerto','marmetos','guacala','cagador','pastrulo','verreta','puteadas','torpe','me canse de',
            'callate','al pedo','baboso','la concha de tu madre','la puta que ta pario', 'la re concha','putos','puto','puta','putas',
            'hijos de las mil putas','la concha de la lora','mucho que mejorar','solo te puede entrener si', 'chupenla', 'chupala','ni borraho',
            'cagon', 'marica','a la mierda' 'maricones', 'maricon', 'cagones', 'cheto', 'cheta', 'chetos', 'chetas', 'boludeando','boludear',
            'hijo de puta','pelotudo','chorro','sos una mierda','boludo del orto', 'zorra','gil','pelotudos','boludos','gilipolla']

goodWords = ['vamooo','amo','amor','precioso','preciosa','preciosos','preciosas','satisfacion','viva amor','enamorado','enamorada',
            'enamorados','enamoradas','agradecidas','agradecidos','agradecido','agradecida','cumplidora','honesta','felices','satisfecho',
             'satisfechos','contentos','contento','recomendable','espectacular','piola','buenos','buenas','buenisimo',
             'buenisima','buenisimos']

## Constants importation Data
pathsData = { 'SENSACINE_SERIES' : "Classifier/data/sensaCineSerie.txt",
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
              'MERCADOLIBRE_NEG' : "Classifier/data/MercadoNeg.txt" }

MERCADO_RATIO = 50000
dataDelimiter = '__dataDelimiter__'

## Constants preProcessing

dirtyReps = re.compile(r'([^lL0])\1{1,}')
dirtySpaces = re.compile(r'(\.|,|:|;|!|\?|\[|\]|\(|\))[A-Za-z0-9]+')
dirtyK = re.compile('[^o]k')
dirtyJaja = re.compile(r'[ja]{5,}')
dirtyJeje = re.compile(r'[je]{5,}')
numbers = re.compile(r'[0-9]+')
uglySeparator = 'THIS-IS-A-SEPARATOR'
pathExpressions = 'Classifier/data/expressions.txt' ## XXX : to fill
exps = set([e.split()[0] for e in open(pathExpressions, encoding='utf8').readlines()])
pathConjug = "C:/Users/ellio/test.json" ## XXX : to fill

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
pathModel = 'sentiment_pipeline.pkl'

## Constants Prediction
decayRate = 8
GOOD_BABY = 'Classifier/img/good_baby.jpg'
BAD_BABY = 'Classifier/img/bad_baby.jpg'