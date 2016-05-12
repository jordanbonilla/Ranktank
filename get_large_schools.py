import os 

def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

if __name__ == "__main__":
	for name in os.listdir("."):
		if os.path.isdir(name):
			print name, get_size(name)