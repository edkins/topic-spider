import sys
if sys.version_info[0] < 3:
	raise ValueError('===> Try python3 <===')

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

def obtainCorpusData():
	print('Processing corpus')
	spidermodel.setCorpusFreqs(corpusFrequencies())

if not spidermodel.loadCorpusData():
	obtainCorpusData()

spidermodel.loadKeywordData()

server.start()

