from bs4 import BeautifulSoup
import sys
import signal
import urllib2 # Used to read the html document
import limit_time
import time
import nltk.data
import mechanize
import re
from html2text import html2text 
UNIVERSITY_LIST_NAME = "world-universities.txt"

def rip_text_from_url(url):
	timeout_duration=3
	class TimeoutError(Exception):
		pass

	def handler(signum, frame):
		raise TimeoutError()

	# set the timeout handler
	signal.signal(signal.SIGALRM, handler) 
	signal.alarm(timeout_duration)
	opener = urllib2.build_opener()

	try:
		br = mechanize.Browser()
		br.set_handle_robots(False)
		br.addheaders = [('User-agent', 'Firefox')]
		html = br.open(url).read().decode('utf-8')
		cleanhtml = clean_html(html)
		text = html2text(cleanhtml).split('\n')
		naturally_spaced = ""
		for line in text:
			naturally_spaced += line + ' '
		organized = sent_detector.tokenize(naturally_spaced)
		print organized
		return organized
	except:
		print "Could not tokenize:", url
		return []

def populate_uni_names():
	base_url = "https://en.wikipedia.org/wiki/"
	all_names = open(UNIVERSITY_LIST_NAME, 'r')
	max_words = -1
	content = all_names.readlines()
	for uni_name in content:
		words = uni_name.split(' ')
		url_end = ''
		for k in range(0, len(words) - 1):
			url_end += words[k] + '_'
		url_end += words[-1]
		url = base_url + url_end
		text = rip_text_from_url(url)
		try:
			print text[0:2]
		except:
			continue
		#names_complete= open("names.complete", 'a+')

if __name__ == "__main__":
	populate_uni_names()