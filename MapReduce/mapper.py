#!/usr/bin/env python
import sys
from signal import signal,SIGPIPE,SIG_DFL

signal(SIGPIPE,SIG_DFL) 

def read_input(file):
	for line in file:
		yield line.split(",")

def main(separator='\t'):
	data = read_input(sys.stdin)
	
	for words in data:
		del words[1] #delete time 
		del words[2] #delete status
		if words[0] == "IP" and words[1] == "URL": #delete the first row
			continue		
		if words[0] == "chmod:" or words[0] == "rm:" or words[0] == "timeout:" or words[0] == "sh:" or words[0] == "[Tue" or words[0] == "[Wed": #delete chomod and rm
			continue	
		if words[1] == "main():":
			continue

		for word in words:
			if word.find("\n") != -1:
				word = word.rstrip('\n') 			
			
			if word.find("GET") != -1 or word.find("POST") != -1:
				print "%s%s%d" % (word,separator,1) #URL:1
			else:
				print "%s%s%d" % (words[words.index(word)-1] + " @"+ word,separator,1) #URL @ip:1
			
		
	#	print "" #add /n

if __name__ == '__main__':
	main()
