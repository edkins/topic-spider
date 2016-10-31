import document
import time
import threading

spiderThread = None
statusString = 'Not running'

def startSpider( request ):
	stopSpider()
	url = request['url']
	print('Starting spider for url ' + url)
	document.visit(url)
	resumeSpider()

class SpiderThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.killing = False

	def run(self):
		global spiderThread
		setStatus('Fetching first url')
		print('Starting spider thread')
		while not self.killing and visitNext():
			time.sleep(0.5)
		spiderThread = None

	def killSpiderThread(self):
		self.killing = True

def visitNext():
	urls = document.unvisitedUrlsWithScores(1)
	if len(urls) < 1:
		setStatus('Nothing left to spider.')
		return False
	if urls[0].score == 0:
		setStatus('Nothing left to spider with a score greater than 0.')
		return False
	url = urls[0].url
	doc = document.visit(url)
	setStatus(doc.status + ' ' + url)
	return True

def stopSpider():
	global spiderThread
	if spiderThread != None:
		statusStirng = 'Terminating spider thread'
		spiderThread.killSpiderThread()
		spiderThread.join()
		spiderThread = None
		setStatus('Not running')
	else:
		print('Spider thread was not running.')

def resumeSpider():
	global spiderThread
	if spiderThread == None:
		setStatus('Starting spider thread')
		spiderThread = SpiderThread()
		spiderThread.start()
	else:
		print('Spider thread already starting, not going to start another.')

def status():
	return statusString

def setStatus(status):
	global statusString
	print('Status: ' + status)
	statusString = status

def isRunning():
	return spiderThread != None

