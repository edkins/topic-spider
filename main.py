import urllib.request
import nltk
import collections
import server
import spidermodel
from bs4 import BeautifulSoup
from bs4 import element

def buildSoupString(soup, indent):
	result = ''
	if type(soup) is element.Tag or type(soup) is BeautifulSoup:
		if soup.name != 'script':
			for child in soup.contents:
				result += buildSoupString(child, indent+1)
			return result
	elif type(soup) is element.NavigableString:
		string = str(soup)
		if not string.startswith('[') or not string.endswith(']'):
			return str(soup).replace('\n','. ') + ' '
	else:
		pass
	return ''

def acceptToken(token):
	return token[0].isalpha()

def corpusFrequencies():
	counts = collections.Counter()
	for fileid in nltk.corpus.brown.fileids():
		for word in nltk.corpus.brown.words(fileid):
			if acceptToken(word):
				counts[word.lower()] += 1
	return counts

print('Processing corpus')
corpusFreq = corpusFrequencies()

print('Downloading')
html = urllib.request.urlopen('https://en.wikipedia.org/wiki/Effective_altruism').read().decode('utf-8')
print('Parsing html')
soup = BeautifulSoup(html,'html.parser')

text = ' '.join(buildSoupString(soup,0).split())

print('Tokenizing')
tokens = nltk.word_tokenize(text)
counts = collections.Counter()
for token in tokens:
	if acceptToken(token):
		counts[token.lower()] += 1

listResult = []
for token in counts:
	score = -counts[token] / (corpusFreq[token] + 1)
	listResult.append((score, token))

print('Adding scored keywords to model.')
spidermodel.addScoredKeywords( listResult )

server.start()

