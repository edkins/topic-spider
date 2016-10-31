import http.server
import spidermodel
import json

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
		if s.path == '/':
			s.path = '/static/index.html'
			return http.server.SimpleHTTPRequestHandler.do_GET(s)
		if s.path.startswith('/static'):
			return http.server.SimpleHTTPRequestHandler.do_GET(s)

	def do_POST(s):
		if s.path == '/v1/relevance':
			s.setRelevance()

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

	def getKeywords(s, relevanceType):
		s.send_response(200)
		s.noCache()
		s.send_header("Content-type", "application/json")
		s.end_headers()
		keywords = spidermodel.topKeywords(100, relevanceFunc(relevanceType))
		jsonText = json.dumps( [ kw.toDictWithoutScore() for kw in keywords ] )
		s.writeln(jsonText)

def start():
	print('Starting server!')
	httpd = http.server.HTTPServer( ('localhost', 8080), MyHandler )
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		print('Quit')
		pass

