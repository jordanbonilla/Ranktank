# encoding=utf8 
from bs4 import BeautifulSoup
import sys
import signal
import urllib2 # Used to read the html document
import limit_time
import time
import nltk.data
import mechanize
import re
import os
from html2text import html2text 
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

UNIVERSITY_LIST_NAME = "world-universities.txt"
UNI_NAMES = {}
MAX_WORDS_PER_UNI = -1
VERBOSE = False




from functools import wraps
import errno
import os
import signal

class TimeoutError(Exception):
    pass

def timeout(seconds=10, error_message=os.strerror(errno.ETIME)):
    def decorator(func):
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result

        return wraps(func)(wrapper)

    return decorator









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
	global VERBOSE
	if VERBOSE is True:
		print "get_phd_pages", name, university
	name = str(name)
	university = str(university)
	search_term = name + ' ' + university + ' phd'
	base_url = "https://www.google.com/search?q="
	search_url = base_url
	words_in_seach_term = search_term.split(' ')
	for word in words_in_seach_term:
		search_url += word + "%20"
	# get url's content
	if VERBOSE is True:
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
			results.append((cite.text).encode('utf-8'))
	return results

def clean_html(html):
	if VERBOSE is True:
		print "clean_html"
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

@timeout(6)
def rip_text_from_url(url):
	if VERBOSE is True:
		print "rip text from url", url

	global VERBSOE

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
		if VERBOSE is True:
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

def in_parens(line, index_of_phd_term, len_phd_word):
	start = index_of_phd_term - 1
	end = index_of_phd_term + len_phd_word
	paren_start = max(0, start)
	paren_end = min(len(line) - 1, end)
	if(line[paren_start] == '(' and line[paren_end] == ')'):
		return True
	else:
		return False

# Get the institution this prof went to school from the text in line
def parse_institution_name(line, phd_word):
	global UNI_NAMES
	global parents
	global all_pseudos
	global VERBOSE
	if("apply" in line):
		return "failure"

	index_of_phd_term = line.index(phd_word)
	if VERBOSE is True:
		print "index of phd term:", index_of_phd_term
	if in_parens(line, index_of_phd_term, len(phd_word)): # if enclosed in parens, we are confident that the uni lies to the left 
		line = line.split("(" + phd_word + ")")[0]
	confounded = False
	confounding = ["b.s.", "bachelors", "masters", "m.s.", "b.a", "m.b.a"]
	for c in confounding:
		if c in line:
			confounded = True
			break

	if confounded is False:
		for phrase in all_pseudos:
			varients = [' ' + phrase + '.', ' ' + phrase + ',', ' ' + phrase + ' ']
			for variant in varients:
				if variant.decode('utf-8') in line:
					return phrase
		return "failure"

	pre = -1
	post = -1
	for i in range(index_of_phd_term, 0, -1):
		char = line[i]
		if (char == ',') or (char == '.'):
			pre = i + 1
			break
	for i in range(index_of_phd_term + len(phd_word), len(line), 1):
		char = line[i]
		if (char == ',') or (char == '.'):
			post = i
			break

	if(pre is not -1 and post is not -1):
		line = line[pre:post]
	if VERBOSE is True:
		print line
	indicies_of_universities = []
	for phrase in all_pseudos:
		varients = [' ' + phrase + '.', ' ' + phrase + ',', ' ' + phrase + ' ']
		for variant in varients:
			if variant.decode('utf-8') in line:
				return phrase
	return "failure"


def find_phd_institution(websites):
	global VERBOSE
	search_words = set(["PhD","Ph.D","Ph.D."])
	for website in websites:
		if VERBOSE is True:
			print website
		if not website.startswith('http'):
			website = '%s%s' % ('http://', website)
		if(website.endswith(".pdf") or website.endswith(".doc") or website.endswith(".ppt") or website.endswith(".docx")):
			if VERBOSE is True:
				print "INVALID EXTENSION:", website
			continue
		else:
			if VERBOSE is True:
				print "OK:", website

			text = rip_text_from_url(website)
			for line in text:
				for word in search_words:
					word = word.lower()
					line = line.lower()
					if word in line:
						return parse_institution_name(line, word) #only care about first occurance to prevent caes like in berkeley where they list phd students
						#if result is not "failure":
						#	return result
	return "failure"

def readDict(filename):
	with open(filename, "r") as f:
		dict = {}
		content = f.readlines()
		for line in content:
			values = line.split("@")
			dict[values[0].lower()] = values[1].lower().replace("\n", "")
		return(dict)

# import shutil
# def cleanup():
# 	curfile = None
# 	parents = readDict("pseudonyms.txt")
# 	all_pseudos = parents.keys()
# 	file = None
# 	unis_visited = {}
# 	for name in os.listdir("."):
# 		if name in unis_visited or name == ".git" or name == "":
# 			continue
# 		else:
# 			unis_visited[name] = True
# 		if os.path.isdir(name):
# 			os.chdir(name)
# 			for folder in os.listdir("."):
# 				while True:
# 					try:
# 						file = open(folder + "/data.txt", "r")
# 					except Exception as e:
# 						print e
# 						e = str(e)
# 						print name, folder

# 						rootDir = folder
# 						data_files_seen = 0
# 						for dirName, subdirList, fileList in os.walk(rootDir):
# 							print('Found directory: %s' % dirName)
# 							for fname in fileList:
# 								if fname == "data.txt":
# 									if(data_files_seen > 0):
# 										print "2 DATA FILES???"
# 										quit()
# 									source = dirName + '/data.txt'
# 									shutil.copy2(source, rootDir)
# 									data_files_seen +=1
# 						filelist = [ f for f in os.listdir(folder) if os.path.isdir(folder + "/" + f) ]
# 						for f in filelist:
# 							print "removing " + folder + "/" + f + " from " + name
# 							shutil.rmtree(folder + "/" + f)
# 					break
# 				print "boop"
# 				#a = file.readlines()
# 				#print a
# 				file.close()
# 			os.chdir("../")


def get_phd(line, school):
	prof_name = line.replace('\n', '')
	current_institute = school

	pages = []
	while True:
		try:
			pages = get_phd_pages(prof_name, current_institute)
		except Exception as e:
			print line, school, e
			time.sleep(10)
			continue
		break

	institute = "failure"
	while True:
		try:
			institute = find_phd_institution(pages)
		except Exception as e:
			print line, school, e
			time.sleep(10)
			continue
		break

	if (institute == "failure"):
		return "UNKNWON"
	else:
		return institute
	# while True:
	# 	try:
	# 		try:
	# 			with time_limit(5):
	# 				pages = get_phd_pages(prof_name, current_institute)
	# 		except TimeoutException, msg:
	# 			print "Timed out"
	# 			break
	# 	except Exception as e:
	# 		print e
	# 		time.sleep(10)
	# 		continue
	# 	break

	# institute = "failure"
	# while True:
	# 	try:
	# 		try:
	# 			with time_limit(5):
	# 				institute = find_phd_institution(pages)
	# 		except TimeoutException, msg:
	# 			print "Timed out"
	# 			break
	# 	except Exception as e:
	# 		print e
	# 		time.sleep(10)
	# 		continue
	# 	break

	# if (institute == "failure"):
	# 	return "UNKNWON"
	# else:
	# 	return institute


if __name__ == "__main__":
	curfile = None
	parents = readDict("pseudonyms.txt")
	all_pseudos = parents.keys()
	file = None
	unis_visited = {}
	for name in os.listdir("."):
		if name in unis_visited or name == ".git" or name == "":
			continue
		else:
			unis_visited[name] = True
		if os.path.isdir(name):
			os.chdir(name)
			for folder in os.listdir("."):
				try:
					file = open(folder + "/data.txt", "r+")
				except Exception as e:
					print e
					e = str(e)
					print name, folder
					quit()
				new_data = ""
				a = file.readlines()
				for line in a:
					start_time = time.time()
					division = line.split('@')
					if("@UNKNWON" in line or line == "\n" or line == "" or line == "@\n"):
						continue
					if len(division) is 1:
						line = line.replace('\n', "")
						line+="@"+str(get_phd(line, name))
					elif len(division) is 2:
						#line = line 
						# REDO WORK (if invalid pseudonym)
						if division[1].replace("\n", "") not in all_pseudos:
							print "name of school that is no longer in all_pseudos:", division[1]
							line = division[0]
							line = line.replace('\n', "")
							line+="@"+str(get_phd(line, name))
						else: # Valid pseudonym. dont redo anything
							line = line.replace('\n', "")
					else:
						print "len(Div) > 2? WTF"
						quit()
					if(division[0] is not ""):
						print name, division, line, time.time() - start_time
						new_data += line + '\n'
				file.seek(0)
				file.truncate()
				file.write(new_data)
				file.close()
			os.chdir("../")



	#rip_text_from_url("http://www.eas.caltech.edu/people/3336/profile")




