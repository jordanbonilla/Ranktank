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
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
UNIVERSITY_LIST_NAME = "us-universities.txt"



def signal_handler(signal, frame):
		print('You pressed Ctrl+C!')
		quit()


def clean_html(html):
	"""
	Copied from NLTK package.
	Remove HTML markup from the given string.

	:param html: the HTML string to be cleaned
	:type html: str
	:rtype: str
	"""

	# First we remove inline JavaScript/CSS:
	cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())
	# Then we remove html comments. This has to be done before removing regular
	# tags since comments can contain '>' characters.
	cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)
	# Next we can remove the remaining tags:
	cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)
	# Finally, we deal with whitespace
	cleaned = re.sub(r"&nbsp;", " ", cleaned)
	cleaned = re.sub(r"  ", " ", cleaned)
	cleaned = re.sub(r"  ", " ", cleaned)
	return cleaned.strip()


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
		return organized
	except:
		print "Unexpected error:", sys.exc_info()[0], url
		return []

def populate_uni_names(uni_name):
	base_url = "https://en.wikipedia.org/wiki/"
	words = uni_name.split(' ')
	url_end = ''
	for k in range(0, len(words) - 1):
		url_end += words[k] + '_'
	url_end += words[-1]
	url = base_url + url_end
	text = rip_text_from_url(url)
	try:
		print text[0]
	except:
		return
	#names_complete= open("names.complete", 'a+')

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	all_names = open(UNIVERSITY_LIST_NAME, 'r')
	max_words = -1
	content = all_names.readlines()
	all_names.close()
	for uni_name in content:
		populate_uni_names(uni_name)
		print "\n@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
		time.sleep(1)
