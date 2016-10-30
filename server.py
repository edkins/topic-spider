import http.server
import spidermodel
import json

def radio(name,value,onchange):
	return '<input type="radio" name="' + name + '" value="' + value + '" onchange="'+onchange+'">'

def image(id,src,width,height,visibility):
	return '<image id="' + id + '"src="' + src + '" width="' + str(width) + '" height="' + str(height) + '" style="visibility:' + visibility + '">'

class MyHandler(http.server.SimpleHTTPRequestHandler):
	def writeln(s,line):
		s.wfile.write((line+'\n').encode('utf-8'))

	def do_GET(s):
		if s.path == '/unrankedKeywords':
			s.getUnrankedKeywords()
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

	def getUnrankedKeywords(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
		s.send_header("Pragma", "no-cache")
		s.send_header("Expires", "0")
		s.end_headers()
		s.writeln('<html>')
		s.writeln('<head>')
		s.writeln('<script src="https://code.jquery.com/jquery-2.2.4.min.js" integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44=" crossorigin="anonymous"></script>')
		s.writeln('<script src="/static/topic.js"></script>')
		s.writeln('</head>')
		s.writeln('<body>')
		s.writeln('<h1>Which topics are relevant?</h1>')
		s.writeln('yes/no<br>')
		keywords = spidermodel.topUnrankedKeywords(100)
		for keyword in keywords:
			s.writeln(radio(keyword.word,'yes','changeRank(event)') + radio(keyword.word,'no','changeRank(event)') +' ' + keyword.word + image('loading-' + keyword.word, '/static/pageloader.gif',16,16,'hidden') + '<br>')
		s.writeln('</body></html>')

def start():
	print('Starting server!')
	httpd = http.server.HTTPServer( ('localhost', 8080), MyHandler )
	httpd.serve_forever()

