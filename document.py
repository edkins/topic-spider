import collections
import urllib.request
import urllib.parse
import urllib.robotparser
import nltk
import bs4
import spidermodel

def buildSoupString(soup, indent):
	result = ''
	if type(soup) is bs4.element.Tag or type(soup) is bs4.BeautifulSoup:
		if soup.name != 'script':
			for child in soup.contents:
				result += buildSoupString(child, indent+1)
			return result
	elif type(soup) is bs4.element.NavigableString:
		string = str(soup)
		if not string.startswith('[') or not string.endswith(']'):
			return str(soup).replace('\n','. ') + ' '
	else:
		pass
	return ''

def acceptToken(token):
	return token[0].isalpha()

# Filter out urls which look like they're pointing to the wrong kind of thing
def suspiciousQuery(query):
	return 'action=' in query

def tidyUrl(url, baseUrl):
	parsedBase = urllib.parse.urlparse(baseUrl)
	parsed = urllib.parse.urlparse(url)
	if not parsed.path:
		return None
	if suspiciousQuery(parsed.query):
		return None
	return urllib.parse.urlunparse((
		parsed.scheme or parsedBase.scheme,
		parsed.netloc or parsedBase.netloc,
		parsed.path,
		parsed.params,
		parsed.query,
		''))

def soupLinks(soup, baseUrl):
	result = []
	if soup.name == 'a' and 'href' in soup.attrs:
		url = tidyUrl( soup['href'], baseUrl )
		if url != None:
			result.append( url )
	if type(soup) is bs4.element.Tag or type(soup) is bs4.BeautifulSoup:
		for child in soup.contents:
			result.extend( soupLinks(child, baseUrl) )
	return result

def robotOk(url):
	parsed = urllib.parse.urlparse(url)
	robotsurl = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
	rp = urllib.robotparser.RobotFileParser(robotsurl)
	rp.read()
	return rp.can_fetch('topic-spider', url)

def fromUrl(url):
	print('Processing ' + url)
	if not robotOk(url):
		raise ValueError('Fails robots.txt check: ' + url)
	html = urllib.request.urlopen(url).read().decode('utf-8')
	soup = bs4.BeautifulSoup(html,'html.parser')
	text = ' '.join(buildSoupString(soup,0).split())
	tokens = nltk.word_tokenize(text)
	counts = collections.Counter()
	for token in tokens:
		if acceptToken(token):
			counts[token.lower()] += 1
	links = soupLinks(soup,url)
	return spidermodel.Document({'url':url, 'wordFreq':dict(counts), 'links':links})

def visit(url):
	if spidermodel.hasDocument(url):
		return

	print('Visiting ' + url)
	doc = fromUrl(url)
	spidermodel.putDocument(doc)

class ScoredDocument:
	def __init__(self, doc, score):
		self.doc = doc
		self.score = score

	def __lt__(self, other):
		return self.score < other.score

	def toDict(self):
		return {'score':self.score, 'url':self.doc.url}

def docScore(doc):
	wordCount = sum(doc.wordFreq.values())
	if wordCount == 0:
		return 0
	score = 0
	for word in doc.wordFreq:
		freq = doc.wordFreq[word]
		score += freq * spidermodel.relevance(word)
	return score / wordCount

def scoreDocument(doc):
	return ScoredDocument( doc, docScore(doc) )

def visitedDocumentsWithScores(count):
	return sorted( [scoreDocument(doc) for doc in spidermodel.allDocuments()] )[0:count]
