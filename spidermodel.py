import os
import json
import document
import urllib.parse
import threading

keywords = {}
corpus = {}
cachedUrls = None
cachedUrlLock = threading.Lock()

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
		if 'ourFreq' in data:
			self.ourFreq = data['ourFreq']
		else:
			self.ourFreq = 0

	def __lt__(self, other):
		return self.score > other.score

	def toDict(self):
		data = {'word':self.word, 'score':self.score, 'ourFreq':self.ourFreq}
		if self.relevance != None:
			data['relevance'] = self.relevance
		return data

def resetScoresToZero():
	for kw in keywords.values():
		kw.score = 0
		kw.ourFreq = 0

def addKeywordScore(word,score,ourFreq):
	if word not in keywords:
		keywords[word] = Keyword({'score':score,'word':word,'ourFreq':ourFreq})
	else:
		keywords[word].score += score
		keywords[word].ourFreq += ourFreq

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

def escapedFilename(url):
	try:
		filename = urllib.parse.quote_plus(url)[0:128]
		return 'data/documents/' + filename
	except KeyError:
		return None

class Document:
	def __init__(self, data):
		self.url = data['url']
		self.wordFreq = data['wordFreq']
		self.links = data['links']
		if 'status' in data:
			self.status = data['status']
		else:
			self.status = 'fetched'

		if 'score' in data:
			self.score = data['score']
		else:
			self.score = 0

	def toDict(self):
		return {'url':self.url,'wordFreq':self.wordFreq,'links':self.links,'status':self.status,'score':self.score}

def hasDocument(url):
	return url in allDocumentUrls()

def putDocument(doc):
	global cachedUrls
	filename = escapedFilename(doc.url)
	if filename == None:
		print('Cannot create file for ' + doc.url)
		return
	out = open(filename,'w')
	json.dump( doc.toDict(), out )
	out.close()
	with cachedUrlLock:
		cachedUrls[doc.url] = doc.score

def getDocument(url):
	filename = escapedFilename(url)
	if filename != None and os.path.exists(filename):
		f = open(filename)
		result = Document(json.load(f))
		f.close()
		return result
	else:
		return Document({'url':url,'wordFreq':{},'links':[],'status':'never visited'})

def allDocumentUrls():
	global cachedUrls
	if cachedUrls == None:
		cachedUrls = {}
		for name in os.listdir('data/documents'):
			f = open('data/documents/'+name)
			obj = json.load(f)
			url = obj['url']
			with cachedUrlLock:
				cachedUrls[url] = obj['score']
			f.close()
	with cachedUrlLock:
		result = list(cachedUrls.keys())
	return result

def allScores():
	global cachedUrls
	allDocumentUrls()
	with cachedUrlLock:
		result = cachedUrls.copy()
	return result

def getDocScore(url):
	allDocumentUrls()
	result = 0
	with cachedUrlLock:
		if url in cachedUrls:
			result = cachedUrls[url]
	return result

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

def ourFreq(word):
	if word in keywords:
		return keywords[word].ourFreq
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

