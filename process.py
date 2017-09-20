# a script to traverse a folder and retrive all bag files
import os
import re

def getFiles(dir_name,regex):
	results = []
	for root, dirs, files in os.walk(dir_name):
		for file in files:
			if regex.match(file):
				results.append(file)
	return results

regex = re.compile(".*?\.bag")
files = getFiles("/media/markus/OS/Users/Sefi/Dropbox/data/",regex)
