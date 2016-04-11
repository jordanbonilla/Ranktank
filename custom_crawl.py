allowed_domains = {'gwu.edu': True, 'byu.edu': True, 'binghamton.edu': True, 'emory.edu': True, 'miami.edu': True, 'osu.edu': True, 'luc.edu': True, 'du.edu': True, 'northwestern.edu': True, 'brandeis.edu': True, 'colorado.edu': True, 'www.wfu.edu': True, 'northeastern.edu': True, 'uconn.edu': True, 'uoregon.edu': True, 'tufts.edu': True, 'berkeley.edu': True, 'ucsd.edu': True, 'yale.edu': True, 'yu.edu': True, 'vt.edu': True, 'nyu.edu': True, 'uchicago.edu': True, 'bu.edu': True, 'clark.edu': True, 'fordham.edu': True, 'nd.edu': True, 'mines.edu': True, 'wisc.edu': True, 'purdue.edu': True, 'syr.edu': True, 'rice.edu': True, 'vanderbilt.edu': True, 'miamioh.edu': True, 'duke.edu': True, 'umass.edu': True, 'washington.edu': True, 'sandiego.edu': True, 'princeton.edu': True, 'fsu.edu': True, 'lehigh.edu': True, 'slu.edu': True, 'unh.edu': True, 'usc.edu': True, 'virginia.edu': True, 'uvm.edu': True, 'missouri.edu': True, 'uiowa.edu': True, 'clemson.edu': True, 'udel.edu': True, 'utk.edu': True, 'ua.edu': True, 'stevens.edu': True, 'columbia.edu': True, 'ucsc.edu': True, 'rutgers.edu': True, 'smu.edu': True, 'georgetown.edu': True, 'drexel.edu': True, 'utexas.edu': True, 'case.edu': True, 'upenn.edu': True, 'wpi.edu': True, 'indiana.edu': True, 'cornell.edu': True, 'usi.edu': True, 'illinois.edu': True, 'tcu.edu': True, 'tulane.edu': True, 'harvard.edu': True, 'utulsa.edu': True, 'marquette.edu': True, 'umich.edu': True, 'ucdavis.edu': True, 'ufl.edu': True, 'brown.edu': True, 'ucla.edu': True, 'msu.edu': True, 'dartmouth.edu': True, 'tamu.edu': True, 'wm.edu': True, 'pepperdine.edu': True, 'cmu.edu': True, 'mit.edu': True, 'rochester.edu': True, 'pitt.edu': True, 'baylor.edu': True, 'caltech.edu': True, 'jhu.edu': True, 'american.edu': True, 'unc.edu': True, 'buffalo.edu': True, 'stonybrook.edu': True, 'auburn.edu': True, 'unl.edu': True, 'bc.edu': True, 'gatech.edu': True, 'uga.edu': True, 'umn.edu': True, 'rpi.edu': True, 'wustl.edu': True, 'stanford.edu': True, 'umd.edu': True, 'psu.edu': True}

from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
import limit_time
import datetime

# a queue of urls to be crawled
new_urls = ['http://princeton.edu', 'http://harvard.edu', 'http://yale.edu', 'http://columbia.edu', 'http://stanford.edu', 'http://uchicago.edu', 'http://mit.edu', 'http://duke.edu', 'http://upenn.edu', 'http://caltech.edu', 'http://jhu.edu', 'http://dartmouth.edu', 'http://northwestern.edu', 'http://brown.edu', 'http://cornell.edu', 'http://vanderbilt.edu', 'http://wustl.edu', 'http://rice.edu', 'http://nd.edu', 'http://berkeley.edu', 'http://emory.edu', 'http://georgetown.edu', 'http://cmu.edu', 'http://ucla.edu', 'http://usc.edu', 'http://www.virginia.edu/', 'http://tufts.edu', 'http://www.wfu.edu', 'http://umich.edu', 'http://bc.edu', 'http://unc.edu', 'http://nyu.edu', 'http://rochester.edu', 'http://brandeis.edu', 'http://wm.edu', 'http://gatech.edu', 'http://case.edu', 'http://ucsd.edu', 'http://usi.edu', 'http://ucsd.edu', 'http://bu.edu', 'http://rpi.edu', 'http://tulane.edu', 'http://ucdavis.edu', 'http://illinois.edu', 'http://wisc.edu', 'http://lehigh.edu', 'http://northeastern.edu', 'http://psu.edu', 'http://ufl.edu', 'http://miami.edu', 'http://osu.edu', 'http://pepperdine.edu', 'http://utexas.edu', 'http://washington.edu', 'http://yu.edu', 'https://gwu.edu', 'http://uconn.edu', 'http://umd.edu', 'http://wpi.edu', 'http://clemson.edu', 'http://purdue.edu', 'http://smu.edu', 'http://syr.edu', 'http://fordham.edu', 'http://uga.edu', 'http://byu.edu', 'http://pitt.edu', 'http://umn.edu', 'http://tamu.edu', 'http://vt.edu', 'http://american.edu', 'http://baylor.edu', 'http://rutgers.edu', 'http://clark.edu', 'http://stevens.edu', 'http://msu.edu', 'http://indiana.edu', 'http://mines.edu', 'http://udel.edu', 'http://umass.edu', 'http://miamioh.edu', 'http://tcu.edu', 'http://uiowa.edu', 'http://ucsc.edu', 'http://marquette.edu', 'http://du.edu', 'http://utulsa.edu', 'http://binghamton.edu', 'http://stonybrook.edu', 'http://colorado.edu', 'http://sandiego.edu', 'http://uvm.edu', 'http://fsu.edu', 'http://slu.edu', 'http://ua.edu', 'http://drexel.edu', 'http://luc.edu', 'http://buffalo.edu', 'http://auburn.edu', 'http://missouri.edu', 'http://unl.edu', 'http://unh.edu', 'http://uoregon.edu', 'http://utk.edu']

# a set of urls that we have already crawled
processed_urls = set()

# Must be a .edu domain and in
def get_domain(url):
	index_of_edu = url.find(".edu")
	if(index_of_edu is -1):
		return "NULL"
	else:
		index_of_domain_start = 0
		i = index_of_edu - 1
		while(i > 0):
			if url[i].isalnum() is False:
				index_of_domain_start = i + 1 
				break
			else:
				i -= 1
	domain = url[index_of_domain_start:index_of_edu + 5]
	#print("index of domain start: %s, index_of_edu: %s, domain: %s" % (index_of_domain_start, index_of_edu, domain))
	return domain

def purge_queue(domain):
	print("Purging Queue of domain: %s" % domain)
	for url in new_urls:
		if domain in url:
			new_urls.remove(url)


# File with all emails parssed in this session
date = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
f = open('parsed emails ' + date + '.txt', 'w')

# process urls one by one until we exhaust the queue
while len(new_urls):

	# move next url from the queue to the set of processed urls
	url = new_urls.pop()
	processed_urls.add(url)

	# extract base url to resolve relative links
	parts = urlsplit(url)
	base_url = "{0.scheme}://{0.netloc}".format(parts)
	domain = get_domain(url)
	path = url[:url.rfind('/')+1] if '/' in parts.path else url

	# get url's content
	print("Processing %s" % url)
	try:
		response = limit_time.timeout(url)
	except:
		# ignore pages with errors
		print("Unable to open link: %s" % url)
		response = None
		continue

	# extract all email addresses and add them into the resulting set
	if(response is None):
		continue

	new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", response.text, re.I))
	for e in new_emails:
		if('alum' in e):
			purge_queue(domain)
			f.write("Domain: %s, %s,\n" % (domain, str(e)))
			f.flush()
			continue

	# create a beutiful soup for the html document
	soup = BeautifulSoup(response.text)

	# find and process all the anchors in the document
	for anchor in soup.find_all("a"):
		# extract link url from the anchor
		link = anchor.attrs["href"] if "href" in anchor.attrs else ''
		# resolve relative links
		if link.startswith('/'):
			link = base_url + link
		elif not link.startswith('http'):
			link = path + link
		# Verify domain
		parts = urlsplit(url)
		base_url = "{0.scheme}://{0.netloc}".format(parts)
		domain = get_domain(url)
		valid_domain = domain in allowed_domains
		# add the new url to the queue if it was not enqueued nor processed yet
		if not link in new_urls and not link in processed_urls and valid_domain:
			#print("accepted link: %s" % link)
			new_urls.insert(0,link)
		#print("REJECTED link: %s, already in queue?: %s, already processed?: %s, valid domain?: %s" % (link, link in new_urls, link in processed_urls, valid_domain))