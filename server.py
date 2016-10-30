import http.server
import spidermodel

class MyHandler(http.server.BaseHTTPRequestHandler):
	def writeln(s,line):
		s.wfile.write((line+'\n').encode('utf-8'))

	def do_GET(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()
		s.writeln('<html><body>')
		s.writeln('<h1>Which topics are relevant?</h1>')
		s.writeln('<form action="/relevance" method="post">')
		s.writeln('<input type="submit"><br>')
		for keyword in spidermodel.topKeywords(100):
			s.writeln('<input type="checkbox" id="kw-'+keyword.word+'"> ' + keyword.word + '<br>')
		s.writeln('</form>')
		s.writeln('</body></html>')

def start():
	print('Starting server!')
	httpd = http.server.HTTPServer( ('localhost', 8080), MyHandler )
	httpd.serve_forever()

