from .constants import *
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from .MarisaTfidfVectorizer import *
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.externals import joblib
class sentimentClassifier:
	def __init__(self, ngram_range = best_params['v__ngram_range'], max_features = best_params['v__max_features'],
							k = best_params['f__k'], alpha = best_params['c__alpha'], lightModel = False):
		self.lightModel = lightModel
		if self.lightModel:
			self.sentiment_pipeline = Pipeline((
			'v', MarisaTfidfVectorizer.MarisaTfidfVectorizer(TfidfVectorizer(ngram_range=ngram_range, \
															 max_features=max_features)),
			'f', SelectKBest(chi2, k=k),
			'c', MultinomialNB(alpha=alpha)
			))
		else:
			self.sentiment_pipeline = Pipeline((
			'v', TfidfVectorizer(ngram_range=ngram_range, max_features=max_features),
			'f', SelectKBest(chi2, k=k),
			'c', MultinomialNB(alpha=alpha)
			))
		self.vocabulary = None
		return
	def fit(self, text, target, verbose=False):
		if verbose:
			print('Proportion of good comments : %f || bad comments : %f' % (target.mean(), 1-target.mean()))
			t = time.time()
			print(' ')
			print('Is fitting ..')
		self.sentiment_pipeline.fit(text, target)
		if verbose:
			print('Fitted in %d minutes' % np.rint(int(time.time()-t)/60))
			print(' ')
			print('Storing the vocabulary ..')
		self.vocabulary = set([e[0] for e in self.sentiment_pipeline.named_steps['v'].vocabulary_.items() if e[1] in set(self.sentiment_pipeline.named_steps['f'].get_support(True))])
		if verbose:
			print('Vocabulary stored')
			print('')
			print('DONE')

	def score(self, text, target, verbose=False):
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
			postProcessing.printResult(text, sentimentPipeline=self.sentiment_pipeline, realVocab=self.vocabulary, verbose=verbose)
		else:
			postProcessing.predict(text, sentimentPipeline=self.sentiment_pipeline, realVocab=self.vocabulary, verbose=verbose)

	def save(self, path = pathModel):
		joblib.dump(self.sentiment_pipeline, path)

		
