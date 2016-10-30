keywords = []

class Keyword:
	def __init__(self, score, word):
		self.score = score
		self.word = word
		self.relevance = None

	def __lt__(self, other):
		return self.score < other.score

	def __repr__(self):
		return self.word + ':' + str(self.relevance)

def addScoredKeywords( newKeywords ):
	"Add (score,keyword) pairs. A lower score is listed first."
	keywords.extend( [Keyword(count,word) for (count,word) in newKeywords] )

def topKeywords( count ):
	return sorted(keywords)[0:count]

def topUnrankedKeywords( count ):
	return [ kw for kw in sorted(keywords) if kw.relevance == None ]

def setRelevance( name, relevance ):
	for kw in keywords:
		if kw.word == name:
			kw.relevance = relevance

def setRelevances( relevances ):
	for relevance in relevances:
		setRelevance( relevance['name'], relevance['relevance'] )
	print( keywords )
