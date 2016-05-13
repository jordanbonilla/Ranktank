from bs4 import BeautifulSoup as BS
import requests
import requests.exceptions
from urlparse import urlparse
from collections import deque
import re
import limit_time
import datetime
import urllib2
from sgmllib import SGMLParser
from urlparse import urljoin
from lxml import etree
import os
import time
import sys
from nltk import tokenize
import signal
import pickle

SLEEP_DURATION = 0

all_encountered_names = {}
ignore = {"colloquially", 'near', "in","Studio", "California","for",'state-assisted',"de","India", "WEZ-lee-in","militaire",'officially,',"Howard",'nationale',"County","La","informally","Cal",'United', "State","sometimes","sic","officially", 'B.S./M.D.',"US","Upstate",'collectively,', "widely",'The', 'Colleges','depending', 'on', 'degree', 'plan', 'disambiguation','States', 'Air', 'Force', "Law","", 'French,', 'National', 'Institute', "Florida","Poly","ha","called","Jay", "John", "Anaheim","Philadelphia","BC", "often", "law","State","nicknamed","MCC", "PCC","Wisconsin","OBU", "University","of","New", "College", "USU", "NLU","MSU", "UT", "st.", "St.","HCC","(formerly,", "renamed", "abbreviated", "originally", "formerly", "commonly", "referred", "to", "and", "Tech", "more", "or", "also", "known", "as", "km", "etc", "accents,", "umlauts,", "etc.", "co-op", 'U', 'FSU'}
all_data = ""
outfilename = ""
parent_nodes = {}
def populate_dict():
	global parent_nodes
	data_lines = all_data.split('\n')
	for line in data_lines:
		phrases = line.split(',')
		parent = phrases[0]
		parent_nodes[parent] = parent
		phrases.remove(phrases[0])
		for phrase in phrases:
			parent_nodes[phrase] = parent

def writeDict(dict, filename):
    with open(filename, "w") as f:
        for i in dict.keys():            
            f.write(i + "@" + dict[i] + '\n')

def readDict(filename):
    with open(filename, "r") as f:
        dict = {}
        content = f.readlines()
        for line in content:
            values = line.split("@")
            dict[values[0]] = values[1].replace("\n", "")
        return(dict)

def write_data():
	populate_dict()
	writeDict(parent_nodes, "pseudonyms.txt")

def signal_handler(signal, frame):
	global outfilename
	global all_data
	print('You pressed Ctrl+C!')
	write_data()
	quit()

#Fetch an HTML file, return the real (redirected) URL and the content.
def fetch_html_page(url):
	content=None
	real_url=url
	disambiguation_needed = None
	try:
		urllib2.socket.setdefaulttimeout(10)  #Bad page, timeout in 10s.
		usock = urllib2.urlopen(url)
		real_url=usock.url  #real_url will be changed if there is a redirection. 
		if "json" in usock.info()['content-type']:
		#if "text/html" in usock.info()['content-type']:
			content=usock.read()	#Fetch it if it is html but not mp3/avi/...
		usock.close()
	### Terminate on CTRL+C sequences, and pass URLError up the stack.
	except (KeyboardInterrupt, urllib2.URLError):
		raise
	if "Search?" in real_url:
		disambiguation_needed = True
	else:
		disambiguation_needed = False
	return (real_url, content, disambiguation_needed)

def purge_duplicate(to_del):
	global all_data
	to_write = ""
	delete_list = [to_del]
	data = all_data.split("\n")
	for line in data:
		line = line.split(",")
		for word in delete_list:
			if word in line:
				line.remove(word)
				print word, "PURGED~~~~"

		for l in line:
			to_write += l + ","
		to_write += "\n"
	all_data = to_write
	

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

#Fetch the hyperlinks. First fetch the content then use URLLister to parse them.
def fetch_links(url):
	links= list()
	disambiguation_needed = None
	try:
		ru,s, disambiguation_needed=fetch_html_page(url)
		if s is not None and disambiguation_needed is True:
			# extract base url to resolve relative links
			parts = urlparse(url)
			base_url = "{0.scheme}://{0.netloc}".format(parts)
			parsed_html = BS(s)
			s = parsed_html.body.find('ul', class_='mw-search-results')
			if(s is None):
				return []
			for anchor in s.find_all("a"):
				# extract link url from the anchor
				link = anchor.attrs["href"] if "href" in anchor.attrs else ''
				# resolve relative links
				if link.startswith('/'):
					link = base_url + link
				elif not link.startswith('http'):
					link = path + link
				links.append(link)


	### Terminate on CTRL+C sequences, and pass URLError up the stack.
	except (KeyboardInterrupt, urllib2.URLError):
		raise
	if disambiguation_needed is False:
		links.append(ru)
	return links

def wiki_search(uni_name):
	base_url = "https://en.wikipedia.org/wiki/Special:Search?search="
	words = re.sub('[^0-9a-zA-Z]+', ' ', uni_name)
	words = words.split()
	url_end = ''
	for k in range(0, len(words) - 1):
		url_end += words[k] + '+'
	url_end += words[-1]
	url = base_url + url_end

	# get url's content
	while(True):
		try:
			links = fetch_links(url)
		except Exception as e:
			print e
			e = str(e)
			if "HTTP Error 404: Not Found" in e:
				links = []
				break
			time.sleep(10)
			continue
		break
	# simplified_links = []
	# for link in links:
	# 	simplified_links.append()
	return links
		# if('alum' in e):
		# 	purge_queue(domain)
		# 	f.write("Domain: %s, %s,\n" % (domain, str(e)))
		# 	f.flush()
		# 	continue

def hasNumbers(inputString):
	return any(char.isdigit() for char in inputString)

# Try to get university pseudonyms given verified Wikipedia page
def get_pseudonyms(url):
	try:
		index_of_university_identifier = ''.join(url).rfind('/')
		university_identifiers = url[index_of_university_identifier+1:].split('_')
		api_url = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro=&explaintext=&titles="
		num_words = len(university_identifiers)
		for i in range(num_words - 1):
			api_url += university_identifiers[i] + "%20"
		api_url += university_identifiers[num_words - 1]
		ru,s, disambiguation_needed=fetch_html_page(api_url)
		s = s.encode('utf-8')
		names = []
		# Get body of message
		begin = s.index('"extract":"')
		begin = begin + 11
		end = s.index('"}}}}')
		s = s[begin: end]
		# Get first sentence (roughly)
		end = min(len(s), 120)
		s = s[0:end]
		#print s
		length = len(s)
		begin = -1
		end = -1
		for i in range(length):
			if(s[i] is '('):
				begin = i + 1
			if(s[i] is ')'):
				end = i
				break
		if begin is not -1 and end is not -1:
			relevant_info = s[begin: end].split(' ')
			if len(relevant_info) > 7:
				return []
			if len(relevant_info) > 4:
				relevant_info = relevant_info[0:4]
			for word in relevant_info:
				if word in all_encountered_names:
					print word, "IN ENCOUNTERED NAMES ################"
					purge_duplicate(word)
					continue
				if word in ignore:
					break
				if word not in all_encountered_names and "\\" not in word and hasNumbers(word) is False and ':' not in word:
					names.append(word)
					all_encountered_names[word] = True
		return names

	### Terminate on CTRL+C sequences, and pass URLError up the stack.
	except (KeyboardInterrupt, urllib2.URLError):
		raise

def record_names():
	# File with all pseudonyms parssed in this session
	global all_data
	global outfilename
	date = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
	outfilename = 'pseudonyms ' + date + '.txt'
	itr = 1
	unis_visited = {}
	for name in os.listdir("."):
		if name in unis_visited or name == ".git" or name == "":
			itr +=1
			continue
		else:
			unis_visited[name] = True
			all_encountered_names[name] = True
		start_time = time.time()
		if os.path.isdir(name):
			links = wiki_search(name)
			if(len(links) > 1): # Only try for the first link
				links = [links[0]]
			pseudonyms = [name] # First name is the node ID (RMP)
			for link in links:
				while True:
					try:
						candidates = get_pseudonyms(link)
					except Exception as e:
						print e
						time.sleep(10)
						continue
					break
				if name in candidates:
					candidates.remove(name)
				pseudonyms = pseudonyms + candidates
				if len(pseudonyms) > 1:
					break
			total_time = time.time() - start_time
			if(total_time < .01): #wierd repeat bug
				continue
			for pseudonym in pseudonyms:
				all_data += pseudonym + ','
		time.sleep(SLEEP_DURATION)

		all_data+='\n'
		sys.stdout.write("Uni #" + str(itr) + ", Iteration duration (s): " + str(total_time) + ", " + str(pseudonyms) + '\n')
		itr += 1	

	write_data()

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	record_names()
	#print get_pseudonyms("https://en.wikipedia.org/wiki/University_of_Virginia")

