import document

def startSpider( request ):
	url = request['url']
	print('Starting spider for url ' + url)
	document.visit(url)
