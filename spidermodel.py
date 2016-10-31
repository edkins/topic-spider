import os
import json

keywords = []

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

def addScoredKeywords( newKeywords ):
	"Add (score,keyword) pairs. A lower score is listed first."
	keywords.extend( [Keyword({'score':score,'word':word}) for (score,word) in newKeywords] )

def topKeywords( count, relevancePred ):
	return [ kw for kw in sorted(keywords) if relevancePred(kw.relevance) ][0:count]

def setRelevance( name, relevance ):
	for kw in keywords:
		if kw.word == name:
			kw.relevance = relevance

def setRelevances( relevances ):
	for relevance in relevances:
		setRelevance( relevance['name'], relevance['relevance'] )
	storeData()

def storeData():
	if not os.path.exists('data'):
		os.mkdir('data')
	jsonText = json.dumps([kw.toDict() for kw in keywords])
	open('data/keywords.json','w').write(jsonText)

def loadData():
	global keywords
	if not os.path.exists('data/keywords.json'):
		print('No data file found')
		return False
	print('Loading data')
	data = json.load(open('data/keywords.json'))
	keywords = [Keyword(d) for d in data]
	return True

