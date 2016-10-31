import collections
import urllib.request
import urllib.parse
import urllib.robotparser
import nltk
import bs4
import spidermodel
import ssl

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
	return 'action=' in query or 'oldid=' in query or 'printable=' in query or 'Special:' in query

def suspiciousPath(path):
	return 'Special:' in path

def urlOk(url):
	parsed = urllib.parse.urlparse(url)
	return not suspiciousQuery( parsed.query ) and not suspiciousPath(parsed.path)

def tidyUrl(url, baseUrl):
	parsedBase = urllib.parse.urlparse(baseUrl)
	parsed = urllib.parse.urlparse(url)
	if not parsed.path:
		return None
	result = urllib.parse.urlunparse((
		parsed.scheme or parsedBase.scheme,
		parsed.netloc or parsedBase.netloc,
		parsed.path,
		parsed.params,
		parsed.query,
		''))
	if urlOk(result):
		return result
	else:
		return None

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
	try:
		print('Processing ' + url)
		if not urlOk(url):
			return spidermodel.Document({'url':url,'wordFreq':{},'links':[],'status':'failed-url'})
		if not robotOk(url):
			return spidermodel.Document({'url':url,'wordFreq':{},'links':[],'status':'failed-robots'})
		html = urllib.request.urlopen(url).read().decode('utf-8')
		soup = bs4.BeautifulSoup(html,'html.parser')
		text = ' '.join(buildSoupString(soup,0).split())
		tokens = nltk.word_tokenize(text)
		counts = collections.Counter()
		for token in tokens:
			if acceptToken(token):
				counts[token.lower()] += 1
		links = soupLinks(soup,url)
		return spidermodel.Document({'url':url, 'wordFreq':dict(counts), 'links':links, 'status': 'fetched', 'score':0})
	except urllib.error.HTTPError:
		return spidermodel.Document({'url':url, 'wordFreq':{},'links':[],'status':'failed-http'})
	except urllib.error.URLError:
		return spidermodel.Document({'url':url, 'wordFreq':{},'links':[],'status':'failed-url'})
	except ssl.CertificateError:
		return spidermodel.Document({'url':url, 'wordFreq':{},'links':[],'status':'failed-cert'})
	except UnicodeDecodeError:
		return spidermodel.Document({'url':url, 'wordFreq':{},'links':[],'status':'failed-unicode'})
	except UnicodeEncodeError:
		return spidermodel.Document({'url':url, 'wordFreq':{},'links':[],'status':'failed-unicode'})

def visit(url):
	if spidermodel.hasDocument(url):
		return

	print('Visiting ' + url)
	doc = fromUrl(url)
	recalculateDocScore(doc)
	spidermodel.putDocument(doc)
	addKeywordScores(doc)
	spidermodel.storeKeywordData()
	return doc

class ScoredUrl:
	def __init__(self, url, score):
		self.url = url
		self.score = score

	def __lt__(self, other):
		return self.score > other.score

	def toDict(self):
		return {'score':self.score, 'url':self.url}

def visitedDocumentsWithScores(count):
	return sorted( [ScoredUrl(doc.url,doc.score) for doc in spidermodel.allDocuments()] )[0:count]

def unvisitedUrlsWithScores(count):
	urlScores = {}
	visitedUrls = set([doc.url for doc in spidermodel.allDocuments()])
	for doc in spidermodel.allDocuments():
		score = doc.score
		for url in doc.links:
			if url in visitedUrls:
				pass
			elif not urlOk(url):
				pass
			elif url in urlScores:
				urlScores[url] = max(urlScores[url], score)
			else:
				urlScores[url] = score
	return sorted( [ScoredUrl(url, urlScores[url]) for url in urlScores] )[0:count]

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

def keywordScore( docFreq, corpusFreq ):
	return docFreq / (corpusFreq + 10)

def addKeywordScores(doc):
	if len(spidermodel.allDocuments()) <= 1:
		multiplier = 1
	else:
		multiplier = pow(doc.score, 2)
	listResult = []
	for word in doc.wordFreq:
		score = keywordScore(doc.wordFreq[word], spidermodel.corpusFreq(word)) * multiplier
		spidermodel.addKeywordScore(word,score,doc.wordFreq[word])

def recalculateKeywordFrequencies():
	spidermodel.resetScoresToZero()
	for doc in spidermodel.allDocuments():
		addKeywordScores(doc)
	spidermodel.storeKeywordData()
	print('Keyword frequencies were recalculated.')

def recalculateDocumentScores():
	for doc in spidermodel.allDocuments():
		recalculateDocScore(doc)
	spidermodel.storeDocData()
	print('Document scores were recalculated.')

def recalculateDocScore(doc):
	if not urlOk(doc.url):
		doc.score = 0
		doc.status = 'failed-url'
		return
	wordCount = sum(doc.wordFreq.values())
	if wordCount == 0:
		return 0
	score = 0
	for word in doc.wordFreq:
		freq = doc.wordFreq[word]
		score += freq * spidermodel.relevance(word)
	doc.score = score / (wordCount + 100)

def wordInfo(word,freq,wordCount):
	relevance = spidermodel.relevance(word)
	contribution = freq * relevance / wordCount
	corpusFreq = spidermodel.corpusFreq(word)
	ourFreq = spidermodel.ourFreq(word)
	return {'word':word,'docFreq':freq,'corpusFreq':corpusFreq,'relevance':relevance,'contribution':contribution,'ourFreq':ourFreq,'wordScore':freq/(ourFreq+1)}

def docInfo(url):
	doc = spidermodel.getDocument(url)
	wordCount = sum(doc.wordFreq.values())
	words = [wordInfo(w, doc.wordFreq[w], wordCount) for w in doc.wordFreq]
	return {'url':url,'status':doc.status,'words':words,'wordCount':wordCount}

def goodlinks(doc,minScore):
	return [url for url in doc.links if spidermodel.getDocument(url).score > minScore]

def links(minScore):
	return [{'url':doc.url,'score':doc.score,'links':goodlinks(doc,minScore)} for doc in spidermodel.allDocuments() if doc.score > minScore]
