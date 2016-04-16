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

UNIVERSITY_LIST_NAME = "world-universities.txt"
UNI_NAMES = {}
MAX_WORDS_PER_UNI = -1

def populate_uni_names():
	global UNI_NAMES
	global MAX_WORDS_PER_UNI
	all_names = open(UNIVERSITY_LIST_NAME, 'r')
	max_words = -1
	content = all_names.readlines()
	for line in content:
		UNI_NAMES[line.lower()] = True
		num_words = len(line.split(' '))
		if num_words > max_words:
			max_words = num_words
	all_names.close()
	print "size of UNI_NAMES:", len(UNI_NAMES)
	print "Max words in a uni name:", max_words
	MAX_WORDS_PER_UNI = max_words


def get_phd_pages(name, university):
	search_term = name + ' ' + university
	base_url = "https://www.google.com/search?q="
	search_url = base_url
	words_in_seach_term = search_term.split(' ')
	for word in words_in_seach_term:
		search_url += word + "%20"
	# get url's content
	print("Processing %s" % search_url)
	### Create opener with Google-friendly user agent
	opener = urllib2.build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]

	### Open page & generate soup
	page = opener.open(search_url)
	soup = BeautifulSoup(page)

	### Parse and find
	### Looks like google contains URLs in <cite> tags.
	### So for each cite tag on the first page, print its contents (url)
	results = []
	for cite in soup.findAll('cite'):
			results.append(str(cite.text))
	return results

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
		print organized
		return organized
	except:
		print "Could not tokenize:", url
		return []

def consecutive_subsequences(words):
	global MAX_WORDS_PER_UNI
	num_words = len(words)
	max_chunk_size = min(num_words, MAX_WORDS_PER_UNI)
	num_phrases = 0
	output = []
	for i in range(1, max_chunk_size):#length of chunk
		for j in range(0, num_words - i - 1):#start index of index
			relevant_words = words[j:j+i]
			this_phrase = ''
			for k in range(0, len(relevant_words) - 1):
				this_phrase += relevant_words[k] + ' '
			this_phrase += relevant_words[-1]
			output.append(this_phrase)
			num_phrases += 1
			if(num_phrases > 10000):
				break
	return output

# Get the institution this prof went to school from the text in line
def parse_institution_name(line, phd_word):
	global UNI_NAMES
	index_of_phd_term = line.index(phd_word)
	print "index of phd term:", index_of_phd_term
	indicies_of_universities = []
	phrases = consecutive_subsequences((line.lower()).split(' '))
	for phrase in phrases:
		if phrase in UNI_NAMES:
			print phrase
	return "failure"



def find_phd_institution(websites):
	search_words = set(["PhD","Ph.D","Ph.D."])
	for website in websites:
		if not website.startswith('http'):
			website = '%s%s' % ('http://', website)
		if(website.endswith(".pdf") or website.endswith(".doc") or website.endswith(".ppt") or website.endswith(".docx")):
			print "INVALID EXTENSION:", website
			continue
		else:
			print "OK:", website
			text = rip_text_from_url(website)
			for line in text:
				for word in search_words:
					word = word.lower()
					line = line.lower()
					if word in line:
						result = parse_institution_name(line, word)
						if result is not "failure":
							print result
							return


if __name__ == "__main__":
	#populate_uni_names()
	#pages = get_phd_pages("Adam Chlipala", "Massachusetts Institute of Technology")
	pages = ["https://www.linkedin.com/in/adamch"]
	find_phd_institution(pages)
	#rip_text_from_url("http://www.eas.caltech.edu/people/3336/profile")




