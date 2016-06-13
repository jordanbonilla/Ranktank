import os
import datetime
import sys
import subprocess

def readDict(filename):
	with open(filename, "r") as f:
		dict = {}
		content = f.readlines()
		for line in content:
			values = line.split("@")
			dict[values[0].lower()] = values[1].lower().replace("\n", "")
		return(dict)

def get_out_degrees(path_to_dirty_results, subject_string):
	parents = None
	try:
		parents = readDict("pseudonyms.txt")
	except Exception as e:
		print e
		quit()
	# cd into dirty folder
	try:
		os.chdir(path_to_dirty_results)
	except:
		print "unable to cd to " + path_to_dirty_results
		sys.exit(-1)
	# For every dirty folder ...
	all_dirty_unis = os.listdir(".")
	unknown_parents = {}
	out_degrees = {}
	################## First pass to get out degree 
	for dirty_uni in all_dirty_unis:
		out_degrees[dirty_uni.lower()] = 0
		# Skip non-dirs
		if os.path.isdir(dirty_uni) is False:
			continue

		all_subjects = os.listdir(path_to_dirty_results + "/" + dirty_uni)
		for subject in all_subjects:
				if subject_string not in subject:
					continue
				# Open dirty data.txt
				file = open(path_to_dirty_results + "/" + dirty_uni + "/" + subject + "/data.txt", "r")
				a = file.readlines()
				encountered = {}
				for line in a:
					division = line.split('@')
					name = division[0]
					if len(division) is not 2:
						continue
						# print "invalid data format: " + str(division)
						# quit()
					if division[1] == "UNKNWON\n":
						continue
					else:
						first = dirty_uni.lower()
						if first not in parents:
							unknown_parents[first] = True
							continue
						try:
							second = parents[division[1].lower().replace("\n", "")]
						except:
							continue
						if name not in encountered:
							encountered[name] = True
						else:
							print "repeated data entry" + dirty_uni + "-" + subject + "-" + second

						out_degrees[first] += 1

				file.close()
		# change dir back to root of dirty folder
		os.chdir(path_to_dirty_results)
	return out_degrees



def clean_results(relative_path_to_dirty_results, subject_string):
	parents = None
	try:
		parents = readDict("pseudonyms.txt")
	except Exception as e:
		print e
		quit()

	date = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
	new_file = open(subject_string + "_extracted.txt", "w")

	new_data = ""
	path_to_dirty_results = "/home/jordan/Documents/Test/Ranktank_done/"#os.getcwd() + str("/") + relative_path_to_dirty_results
	# cd into dirty folder
	try:
		os.chdir(path_to_dirty_results)
	except:
		print "unable to cd to " + path_to_dirty_results
		sys.exit(-1)
	# For every dirty folder ...
	all_dirty_unis = os.listdir(".")
	unknown_parents = {}
	MIN_HITS = 5
	out_degrees = get_out_degrees(path_to_dirty_results, subject_string)
	################## Get results 
	for dirty_uni in all_dirty_unis:
		# Skip non-dirs
		if os.path.isdir(dirty_uni) is False:
			continue
		first = dirty_uni.lower()
		if out_degrees[first] < MIN_HITS:
			continue
		all_subjects = os.listdir(path_to_dirty_results + "/" + dirty_uni)
		for subject in all_subjects:
			if subject_string not in subject:
				continue
			# Open dirty data.txt
			file = open(path_to_dirty_results + "/" + dirty_uni + "/" + subject + "/data.txt", "r")
			a = file.readlines()
			encountered = {}
			for line in a:
				division = line.split('@')
				name = division[0]
				if len(division) is not 2:
					continue
					# print "invalid data format: " + str(division)
					# quit()
				if division[1] == "UNKNWON\n":
					continue
				else:
					first = dirty_uni.lower()
					if first not in parents:
						unknown_parents[first] = True
						continue
					try:
						second = parents[division[1].lower().replace("\n", "")]
					except:
						continue
					if name not in encountered:
						new_line =  first + "@" + second + '\n'
						new_data += new_line
						encountered[name] = True
					else:
						print "repeated data entry" + dirty_uni + "-" + subject + "-" + second
						
			file.close()
		# change dir back to root of dirty folder
		os.chdir(path_to_dirty_results)

################# print any errors and write results
	pars = unknown_parents.keys()
	for p in pars:
		print p
	# Write the cleaned data to clean
	new_file.write(new_data)
	new_file.close()
	return out_degrees

from operator import itemgetter
def sort_results(raw_output, subject, outdegrees, norm_bool):
	done = []
	max_unis = 10
	output = raw_output.split("\n")
	for line in output:
		if line == "":
			continue
		parts = line.split(" = ")
		if len(parts) is not 2:
			print "Invalid file format!!!: " + line
			nf = open("examine.txt", "w")
			nf.write(raw_output)
			nf.close()
			quit()
		name = parts[0]
		numeric = float(parts[1])
		if norm_bool is 1:
			od = outdegrees[name]
			if od is 0:
				numeric = -1
			else:
				numeric = numeric / od
		done.append((name, numeric))

	done = sorted(done, key=itemgetter(1), reverse=True)
	print "Top " + str(max_unis) + " " + subject + " Universities"
	for i in range(max_unis):
		try:
			#print str(i+1) + ") " + done[i][0] #+ " - " + str(done[i][1]) 
			print done[i][0].title()
		except:
			print i, done[i]



if __name__ == "__main__":
	if len(sys.argv) is not 3:
		print "python extract <relative path to folder of unprocessed data> <normalize?>"
		sys.exit(-1)
	else:
		norm_bool = int(sys.argv[2])
		base_dir = os.getcwd()
		subjects = ["English", "Philosophy", "Liberal", "Psychology", "Econ", "Business", "History", "Bio", "Chem", "Physics", "Math", "Computer", "Mechanical", "Electrical", "Engineering", ""]
		for s in subjects:
			path_to_dirty_results = sys.argv[1]
			outdegrees = clean_results(path_to_dirty_results, s)
			os.chdir(base_dir)
			fname = s + "_extracted.txt"
			bashCommand = "./pagerank -d @ " + fname
			process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
			output = process.communicate()[0]
			sort_results(output, s, outdegrees, norm_bool)
