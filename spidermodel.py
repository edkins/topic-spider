import os
import json
import document

keywords = {}
documents = {}
corpus = {}

#######################
#
# Keyword
#
#######################


class Keyword:
	def __init__(self, data):
		self.score = data['score']
		self.word = data['word']
		if 'relevance' in data:
			self.relevance = data['relevance']
		else:
			self.relevance = None

	def __lt__(self, other):
		return self.score < other.score

	def __repr__(self):
		return self.word + ':' + str(self.relevance) + ':' + str(self.score)

	def toDict(self):
		data = {'score':self.score, 'word':self.word}
		if self.relevance != None:
			data['relevance'] = self.relevance
		return data

	def toDictWithoutScore(self):
		data = {'word':self.word}
		if self.relevance != None:
			data['relevance'] = self.relevance
		return data

def resetScoresToZero():
	for kw in keywords.values():
		kw.score = 0

def addKeywordScore(word,score):
	if word not in keywords:
		keywords[word] = Keyword({'score':score,'word':word})
	else:
		keywords[word].score += score

def topKeywords( count, relevancePred ):
	return [ kw for kw in sorted(keywords.values()) if relevancePred(kw.relevance) ][0:count]

def _setRelevance( name, relevance ):
	if name in keywords:
		keywords[name].relevance = relevance

def setRelevances( relevances ):
	for relevance in relevances:
		_setRelevance( relevance['name'], relevance['relevance'] )
	storeKeywordData()

def relevance( word ):
	if word not in keywords:
		return 0
	result = keywords[word].relevance
	if result == None:
		return 0
	return result

def storeKeywordData():
	if not os.path.exists('data'):
		os.mkdir('data')
	jsonText = json.dumps([kw.toDict() for kw in keywords.values()])
	open('data/keywords.json','w').write(jsonText)

def loadKeywordData():
	global keywords
	if not os.path.exists('data/keywords.json'):
		print('No keyword data file found')
		return False
	print('Loading keyword data')
	data = json.load(open('data/keywords.json'))
	keywords = {d['word']:Keyword(d) for d in data}
	return True

#######################
#
# Document
#
#######################


class Document:
	def __init__(self, data):
		self.url = data['url']
		self.wordFreq = data['wordFreq']
		self.links = data['links']

	def toDict(self):
		return {'url':self.url,'wordFreq':self.wordFreq,'links':self.links}

def storeDocData():
	if not os.path.exists('data'):
		os.mkdir('data')
	jsonText = json.dumps([doc.toDict() for doc in documents.values()])
	open('data/documents.json','w').write(jsonText)

def loadDocData():
	global documents
	if not os.path.exists('data/documents.json'):
		print('No document data file found')
		return False
	print('Loading document data')
	data = json.load(open('data/documents.json'))
	documents = {d['url']: Document(d) for d in data}
	return True

def hasDocument(url):
	return url in documents

def putDocument(doc):
	documents[doc.url] = doc
	storeDocData()

def allDocuments():
	return documents.values()

#######################
#
# Corpus
#
#######################

def setCorpusFreqs(freqs):
	global corpus
	corpus = dict(freqs)
	storeCorpusData()

def corpusFreq(word):
	if word in corpus:
		return corpus[word]
	return 0

def storeCorpusData():
	if not os.path.exists('data'):
		os.mkdir('data')
	jsonText = json.dumps( [{'word':word,'freq':corpus[word]} for word in corpus] )
	open('data/corpus.json','w').write(jsonText)

def loadCorpusData():
	global corpus
	if not os.path.exists('data/corpus.json'):
		print('No corpus data file found')
		return False
	print('Loading corpus data')
	data = json.load(open('data/corpus.json'))
	corpus = {c['word']: c['freq'] for c in data}
	return True

