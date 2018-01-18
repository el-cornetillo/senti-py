# senti-py
A sentiment Analysis classifier in spanish

Author : Elliot Hofman

This is a package to perform sentiment analysis in spanish.

It's built on top of scikit-learn and NLTK.

Marisa-trie is used to make the final trained model.pkl memory-efficient ( from 150Ko to 28Ko!)

## INSTALLATION

It's as simple as : 

1/ Open terminal

2/ Run 'pip install spanish_sentiment_analysis'

## USAGE

See the demo_classifier.ipynb notebook to see how to use the classifier.


## THE DATA

The model is fed data crawled from various websites : 
Trip Advisor
PedidosYa

Apestan

QuejasOnline

MercadoLibre

SensaCine

OpenCine

TASS

Twitter

(See the files under /crawlers if interested)
This represents roughly 1M samples.

## THE MODEL

The model is a simple pipeline that includes : 

- A vectorizer : go from the text/string representation of the comment to a vectorized representation.
				This is done with a TfIdfVectorizer
- A feature Selector : The vectorizer will output a n_samples*n_features very sparse matrix (scipy sparse 					matrices are already used by the sklean algorithm). This will reduce the number n_features, 				checking weather a feature is relevant or not.
- A classifier : The model used is a Multinomial Naive Bayes, which performs really well for text 
				classification.

The parameters and hyper-parameters of this pipeline are found by the use of a GridSearch K - cross validation with K = 10

## THE PREPROCESSING

All the comments are preprocessed before the training is done :
- They are set to lowercase
- Accents are removed and replaced (í ==>i, etc)
- 're' and '100%' are replaced by 'muy', which most of the time will have the same meaning in spanish
- ' x ' are replaced by ' por ', ' q ' and ' k ' by 'que'
- Regex is used to replace all possible forms of 'jajajajaja', 'ajajaaaajjaj', 'jjjjaajj', 'ajaja', 'jejejej', etc ...  by the normalized form 'jaja'
- Regex is used to replace duplicated characters ('Que buenoooooo' -> 'Que bueno' etc), paying attention to the special case of the 'l' (It is actually normal in spanish to have words with repeated 'll')
- Reg ex is used to clean spaces ('No me gusto la comida.Vos que opinas?Sisi estuvo mala estoy de acuerdo' -> No me gusto la comida. Vos que opinas? Sisi estuvo mala estoy de acuerdo)
- Regex is used to clean 'k' (askeroso - > asqueroso)
- Reg ex is used to clean numbers (remove them all, except the 100% that is already replaced before)
- a dictionnary of spanish expressions is used to factorize expressions in the comments (por supuesto -> por_supuesto, poco a poco -> poco_a_poco, etc...)
- a dictionnary crawled from the web is used to set a list of chosen verbs to their infinitive form
('me cayo mal la comida'-> 'me caer mal la comida', etc ...)
- a function is applied to apply 'not_' to the words contained between a negation term and min(3, a stopNeg term) terms further. (Las papas no son ricas -> Las papas no not_son not_ricas) 
	The model will then learn that the fictive word 'not_ricas' is associated to a bad sentiment.
- a list of customed neutral words is used to remove useless words from the comment before the prediction is made.

## THE PREDICTION

The prediction is calculated with a few rules:
- If 'pero' is found in the comment to classify,
	preScore = prediction(sentence before the 'pero')
	postScore = prediction(sentence before the 'pero')

	and a barycenter of those two quantities is calculated ((decayRate-t)*preScore + t*postScore)/decayRate
	so that the score remains from the same side of 0.5 than postScore
	This because the comments might say something kind of good, and then finish 'pero ...' and say something kind of good. In this case, usually the global sentiment of the comment is carried by the second part of the phrase.
- If 'muy' is found in the comment to classify:
	importantScore = prediction(next word just after 'muy' if that word is an adjective)
	score = globalScore of the sentence

	and the same barycenter method is used so that the final prediction will predict the same thing as the important word placed after the 'muy'.
	This is used because the comment might say a lot of things ('bla balab blalal') and the classifier could eventually get confused (if there was some piece of irony, a too big quantity of unknown words, ...), but if the comment started by ('Muy recomendable') anyway it will know the comment is good.
- The comments are processed the same way the training data was prepared, and the words that are not in the vocabulary are removed, to reduce the noise that they bring to the comment.



