### So I need to tell Python where to look.
from bs4 import BeautifulSoup
import sys
sys.path.append("./BeautifulSoup")
import urllib2 # Used to read the html document
import limit_time

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
	### So for each cite tag on each page (10), print its contents (url)
	results = []
	for cite in soup.findAll('cite'):
			results.append(cite.text)
	return results

def find_phd_institution(websites):
	search_words = set(["PhD","Ph.D","Ph.D."])
	for website in websites:
		response = limit_time.timeout(website)
		if(response is None):
			print "NO SOUP for", website
			continue
		else:
			soup = BeautifulSoup(response.text)
			for key in search_words:
				print soup.body.findAll(text=key)
		time.sleep(.5)



if __name__ == "__main__":
	pages = get_phd_pages("Adam Wierman", "California Institute of Technology")
	find_phd_institution(pages)