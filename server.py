import http.server
import spidermodel
import json
import engine
import document

def radio(name,value,onchange):
	return '<input type="radio" name="' + name + '" value="' + value + '" onchange="'+onchange+'">'

def image(id,src,width,height,visibility):
	return '<image id="' + id + '"src="' + src + '" width="' + str(width) + '" height="' + str(height) + '" style="visibility:' + visibility + '">'

def relevanceFunc(relevanceType):
	if relevanceType == 'unranked':
		return lambda r: r == None
	if relevanceType == 'relevant':
		return lambda r: r != None and r >= 0.5
	if relevanceType == 'irrelevant':
		return lambda r: r != None and r < 0.5
	raise ValueError('Unrecognized relevance type: ' + str(relevanceType) )

class MyHandler(http.server.SimpleHTTPRequestHandler):
	def writeln(s,line):
		s.wfile.write((line+'\n').encode('utf-8'))

	def do_GET(s):
		if s.path.startswith('/v1/keywords/'):
			s.getKeywords( s.path[len('/v1/keywords/'):] )
		if s.path.startswith('/v1/documents/'):
			s.getDocuments( s.path[len('/v1/documents/'):] )
		if s.path == '/v1/spider/status':
			s.spiderStatus()
		if s.path == '/v1/links':
			s.getLinks()

		if s.path == '/':
			s.path = '/static/index.html'
			return http.server.SimpleHTTPRequestHandler.do_GET(s)
		if s.path.startswith('/static'):
			return http.server.SimpleHTTPRequestHandler.do_GET(s)

	def do_POST(s):
		if s.path == '/v1/relevance':
			s.setRelevance()
		elif s.path == '/v1/docinfo':
			s.getDocInfo()
		elif s.path == '/v1/spider/visit':
			s.spider()
		elif s.path == '/v1/spider/resume':
			s.resumeSpider()
		elif s.path == '/v1/spider/stop':
			s.stopSpider()
		elif s.path == '/v1/spider/stopAndRecalculate':
			s.stopSpiderAndRecalculate()

	def getLinks(s):
		s.forJson()
		jsonText = json.dumps(document.links(0.005))
		s.writeln(jsonText)

	def getDocInfo(s):
		length = int(s.headers['content-length'])
		request = json.loads(s.rfile.read(length).decode('utf-8'))
		jsonText = json.dumps(document.docInfo(request['url']))
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
		s.writeln(jsonText)

	def getDocuments(s, docType):
		docs = []
		if docType == 'visited':
			docs = document.visitedDocumentsWithScores(100)
		elif docType == 'unvisited':
			docs = document.unvisitedUrlsWithScores(100)
		else:
			raise ValueError('Unrecognized document type: ' + str(docType) )
		s.forJson()
		jsonText = json.dumps( [doc.toDict() for doc in docs] )
		s.writeln(jsonText)

	def spiderStatus(s):
		status = engine.status()
		running = engine.isRunning()
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
		jsonText = json.dumps( {'status':status, 'running':running} )
		s.writeln(jsonText)

	def resumeSpider(s):
		engine.resumeSpider()
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
		s.writeln('{}')

	def stopSpider(s):
		engine.stopSpider()
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
		s.writeln('{}')

	def stopSpiderAndRecalculate(s):
		engine.stopSpider()
		document.recalculateDocumentScores()
		document.recalculateKeywordFrequencies()
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
		s.writeln('{}')

	def spider(s):
		length = int(s.headers['content-length'])
		request = json.loads(s.rfile.read(length).decode('utf-8'))
		engine.startSpider(request)
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
		s.writeln('{}')

	def setRelevance(s):
		length = int(s.headers['content-length'])
		relevances = json.loads(s.rfile.read(length).decode('utf-8'))
		spidermodel.setRelevances(relevances)
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
		s.writeln('{}')

	def noCache(s):
		s.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.send_header("Expires", "0")

	def forJson(s):
		s.send_response(200)
		s.noCache()
		s.send_header("Content-type", "application/json")
		s.end_headers()

	def getKeywords(s, relevanceType):
		s.forJson()
		keywords = spidermodel.topKeywords(100, relevanceFunc(relevanceType))
		jsonText = json.dumps( [ kw.toDict() for kw in keywords ] )
		s.writeln(jsonText)

def start():
	print('Starting server!')
	httpd = http.server.HTTPServer( ('localhost', 8080), MyHandler )
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		engine.stopSpider()
		print('Quit')
		pass

