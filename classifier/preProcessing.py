from .constants import *

class Processor:
	def __init__(self, neutralWords=neutralWords, verbose=False):
		self.verbose = verbose
		self.neutralWords = neutralWords
		return

	def binarize(self,r):
	    if r>=4:
	        return 1
	    elif r<=2.5:
	        return 0
	    else:
	        return np.nan
	def replaceAccents(self,word):
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

	def processDetails(self,word):
	    word = word.replace(' re comen',' recomen')
	    word = word.replace(' re ',' muy ')
	    word = word.replace(' 100% ', ' muy ')
	    word = word.replace('mercado libre', uglySeparator.join(['mercado','libre']))
	    word = word.replace(' x ',' por ')
	    word = word.replace(' q ', ' que ')
	    word = word.replace(' k ', ' que ')
	    return word

	def processJaja(self,word):
	    while dirtyJaja.search(word)!=None:
	        word = word.replace(dirtyJaja.search(word).group(),'jaja')
	    while dirtyJeje.search(word)!=None:
	        word = word.replace(dirtyJeje.search(word).group(),'jaja')
	    return word    
    
	def processRep(self,word):
	    '''la doble L atencion !!!!'''
	    while dirtyReps.search(word)!=None:
	        word = word.replace(dirtyReps.search(word).group(),dirtyReps.search(word).group()[0])
	    return word
	def processSpaces(self,word):
	    while dirtySpaces.search(word)!=None:
	        word = word.replace(dirtySpaces.search(word).group()[0],dirtySpaces.search(word).group()[0]+' ')
	    return word
	def processK(self,word):
	    while dirtyK.search(word)!=None:
	        word = word.replace(dirtyK.search(word).group(),dirtyK.search(word).group()[0]+'qu')
	    return word
	def processNumbers(self,word):
	    #word = word.replace('1000',uglySeparator+'mil')
	    #word = word.replace('100',uglySeparator+'cien')
	    #word = word.replace('10',uglySeparator+'diez')
	    while numbers.search(word)!=None:
	        word = word.replace(numbers.search(word).group(),'')
	    #word = word.replace(uglySeparator+'mil','1000')
	    #word = word.replace(uglySeparator+'cien','100')
	    #word = word.replace(uglySeparator+'diez','10')    
	    return word
	def processPoint(self,x):
	    if len(x)==0:
	        return x
	    else:
	        if x[-1] in stopNeg:
	            return x
	        else:
	            return x+'.'
	def processNeg(self,tokens):
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

	def processExps(self,x):
	    foundMatch = any(e in x.replace(' ','_') for e in exps)
	    if foundMatch==False:
	        return x
	    else:
	        x = x.replace(' ','_')
	        matches = [e for e in exps if e in x]
	        for e in matches:
	            x = x.replace(e,uglySeparator.join(e.split('_')))
	        return x.replace('_',' ')
	def replaceVerbs(self,x):
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
        
	def process(self,x):
	    try:
	        str(x).replace('\r','').replace('\n','')
	        x = self.replaceAccents(x.lower())
	        x = self.processNumbers(x)
	        x = self.processDetails(x)
	        x = self.processRep(x)
	        x = self.processJaja(x)
	        x = self.processSpaces(x)
	        x = self.processPoint(x)
	        x = self.processExps(x)
	        x = self.processK(x)
	        tokens = word_tokenize(self.replaceVerbs(x))
	        tokens = [t for t in tokens if t not in neutralWords]
	        tokens = self.processNeg(tokens)
	        #tokens = [t for t in tokens if t not in uselessWords]
	    except:
	        tokens = ['NC']
	    return ' '.join(str(re.sub('[?;,;:!"\(\)\'.]','',' '.join(tokens))).split()).replace(uglySeparator,'_')

	def processDocs(self, text, target):
		df = pd.DataFrame(data = list(zip(text,target)), columns = ['comment', 'rating'])
		if self.verbose:
			print('Number of comments before binarize : %d' % df.shape[0])
		df['target'] = df['rating'].apply(lambda x : self.binarize(x))
		df.dropna(how='any', inplace=True)
		if self.verbose:
			print('Number of comments after binarize : %d' % df.shape[0])
		text = [self.process(e) for e in tqdm(df['Comment'])]
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
		return text, target