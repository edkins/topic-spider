import document
import time
import threading

spiderThread = None

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
		print('Starting spider thread')
		while not self.killing and visitNext():
			time.sleep(0.5)
	def killSpiderThread(self):
		self.killing = True

def visitNext():
	urls = document.unvisitedUrlsWithScores(1)
	if len(urls) < 1:
		print('Nothing left to spider.')
		return False
	if urls[0].score == 0:
		print('Nothing left to spider with a score greater than 0.')
		return False
	url = urls[0].url
	document.visit(url)
	return True

def stopSpider():
	global spiderThread
	if spiderThread != None:
		spiderThread.killSpiderThread()
		spiderThread.join()
		spiderThread = None
	else:
		print('Spider thread was not running.')

def resumeSpider():
	global spiderThread
	if spiderThread == None:
		spiderThread = SpiderThread()
		spiderThread.start()
	else:
		print('Spider thread already starting, not going to start another.')
