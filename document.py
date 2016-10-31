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
	addKeywordScores(doc)
	spidermodel.storeKeywordData()

class ScoredUrl:
	def __init__(self, url, score):
		self.url = url
		self.score = score

	def __lt__(self, other):
		return self.score > other.score

	def toDict(self):
		return {'score':self.score, 'url':self.url}

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
	return ScoredUrl( doc.url, docScore(doc) )

def visitedDocumentsWithScores(count):
	return sorted( [scoreDocument(doc) for doc in spidermodel.allDocuments()] )[0:count]

def unvisitedUrlsWithScores(count):
	urlScores = {}
	visitedUrls = set([doc.url for doc in spidermodel.allDocuments()])
	for doc in spidermodel.allDocuments():
		score = docScore(doc)
		for url in doc.links:
			if url in visitedUrls:
				pass
			elif url in urlScores:
				urlScores[url] = max(urlScores[url], score)
			else:
				urlScores[url] = score
	return sorted( [ScoredUrl(url, urlScores[url]) for url in urlScores] )

def obtainKeywordData(url):
	print('Downloading')
	html = urllib.request.urlopen(url).read().decode('utf-8')
	print('Parsing html')
	soup = BeautifulSoup(html,'html.parser')

	text = ' '.join(buildSoupString(soup,0).split())

	print('Tokenizing')
	tokens = nltk.word_tokenize(text)
	counts = collections.Counter()
	for token in tokens:
		if acceptToken(token):
			counts[token.lower()] += 1

def addKeywordScores(doc):
	if len(spidermodel.allDocuments()) <= 1:
		multiplier = 1
	else:
		multiplier = docScore(doc)
	listResult = []
	for word in doc.wordFreq:
		score = doc.wordFreq[word] * multiplier / (spidermodel.corpusFreq(word) + 1)
		spidermodel.addKeywordScore(word,score)

def recalculateKeywordFrequencies():
	spidermodel.resetScoresToZero()
	for doc in spidermodel.allDocuments():
		addKeywordScores(doc)
	spidermodel.storeKeywordData()
	print('Keyword frequencies were recalculated.')
