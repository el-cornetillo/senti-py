from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import marisa_trie
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