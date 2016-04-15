import urllib2
import time
import sys
import signal
import os

prof_id = -1
SLEEP_INTERVAL = .4
CACHE_FILE_NAME = "highest_explored_index.txt"

def signal_handler(signal, frame):
		global prof_id
		global CACHE_FILE_NAME

		print('You pressed Ctrl+C!')
		print('updating and closing index cache file')
		index_cache_file = open(CACHE_FILE_NAME,"w")
		index_cache_file.write(str(prof_id - 1))
		index_cache_file.flush()
		index_cache_file.close()
		quit()

def update_cache(prof_id):
	index_cache_file = open(CACHE_FILE_NAME,"w")
	index_cache_file.write(str(prof_id))
	index_cache_file.flush()
	index_cache_file.close()

def store_data(this_result):
	name = this_result[0]
	department = this_result[1]
	host_uni = this_result[2]
	folder = host_uni + '/' + department
	if not os.path.exists(folder):
		os.makedirs(folder)
	data_file = open(folder + '/' + "data.txt","a+")
	# Don't double count
	for line in data_file:
		if name in line:
			sys.stdout.write("PROFESSOR: " + str(this_result) + ", ID: " + str(prof_id) + " ALREADY ENCOUNTERED, ")
			data_file.close()
			return
	data_file.write(name + '\n')
	data_file.close()
	sys.stdout.write(str(this_result) + ", Prof ID: " + str(prof_id) + ", ")

def get_professor_info(url):
	response = urllib2.urlopen(url)
	html = response.read()
	# Ensure valid RMP url
	if "Page Not Found" in html:
		return []

	num_chars = len(html)
	prop3_start = html.index('"prop3"')
	prop6_start = html.index('"prop6"')
	prop7_start = html.index('"prop7"')


	department_start = prop3_start + 10
	i = department_start
	while(html[i] is not '"'):
		i += 1
	department = html[department_start: i].strip()

	host_uni_start = prop6_start + 10
	i = host_uni_start
	while(html[i] is not '"'):
		i += 1
	host_uni = html[host_uni_start: i].strip()

	name_start = prop7_start + 10
	i = name_start
	while(html[i] is not '"'):
		i += 1
	name = html[name_start: i].strip()

	info = []
	info.append(name)
	info.append(department)
	info.append(host_uni)
	return info

if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	# Cache the highest id we crawled
	index_cache_file = open(CACHE_FILE_NAME,"a+")
	if(os.path.getsize(CACHE_FILE_NAME) is 0):
		prof_id = 1
	else:
		prof_id = int((index_cache_file.readlines())[0])
	print("Beginning from index", prof_id)
	index_cache_file.close()

	base_url = "http://www.ratemyprofessors.com/ShowRatings.jsp?tid="
	for i in range(prof_id, 200000):
		start_time = time.time()
		next_url = base_url + str(prof_id)
		this_result = get_professor_info(next_url)
		if len(this_result) is 3:
			store_data(this_result)
		time.sleep(SLEEP_INTERVAL)
		prof_id += 1
		update_cache(prof_id)
		sys.stdout.write("Iteration duration (s): " + str(time.time() - start_time) + '\n')
