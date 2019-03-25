#!/usr/bin/env python
import sys
from collections import OrderedDict
from itertools import groupby
from operator import itemgetter

def read_mapper_output(file,separator='\t'):
	for line in file:
		yield line.rstrip().split(separator,1)

def main(separator = '\t'):
	data = read_mapper_output(sys.stdin,separator)
	url_count = OrderedDict()
	url_ip_count = OrderedDict()
	url_count_new = OrderedDict()

	for url,count_str in data:		
		if url.find("@") != -1: #count_str includes ip address
			ip = url.split()[3]
			url = url.split()[1] + ip #URL@ip
			
			count = int(count_str)
			if url not in url_ip_count:
				url_ip_count[url] = count
			else:
				url_ip_count[url] += count

			continue

		
		url = url.split()[1] #delete GET/HOST and HTTP
		count = int(count_str)
		if url not in url_count:
			url_count[url] = count
		else:
			url_count[url] += count
		
	for url,total_count in url_count.items():
		print "PV:%s%s%d" % (url,separator,total_count)

	for url_ip,total_count in url_ip_count.items(): #calculate independent ip without repetition
		url = url_ip.split("@")[0]
		
		if url not in url_count_new:
			url_count_new[url] = 1
		else:
			url_count_new[url] += 1

	for url,total_count in url_count_new.items():
		print "IP:%s%s%d" % (url,separator,total_count)
	

if __name__ == "__main__":
	main()
