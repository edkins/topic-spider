keywords = []

class Keyword:
	def __init__(self, score, word):
		self.score = score
		self.word = word

	def __lt__(self, other):
		return self.score < other.score

def addScoredKeywords( newKeywords ):
	"Add (score,keyword) pairs. A lower score is listed first."
	keywords.extend( [Keyword(count,word) for (count,word) in newKeywords] )

def topKeywords( count ):
	return sorted(keywords)[0:count]

