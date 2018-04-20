# -*- coding: utf-8 -*-
import os
import re
import sys
import csv
import requests
import lxml.html


def get_web_info(app_name, url):
	r = requests.get(url)
	content = r.content.decode("utf-8")
	tree = lxml.html.fromstring(content)
	attention = tree.xpath("/html/body/div[2]/div/@class")[0]
	if attention == "no-result" :
		data = [app_name, 'null', 'null', 'null']
		return data
	else:
		web_version = tree.xpath("/html/body/div[2]/div[2]/div/div/ul/li/div/div[3]/a/@data_versionname")[0]
		web_package_name = tree.xpath("/html/body/div[2]/div[2]/div/div/ul/li/div/div[3]/a/@data_package")[0]
		web_href = tree.xpath("/html/body/div[2]/div[2]/div/div/ul/li/div/div[2]/div/a/@href")[0]
		web_element = web_href.split('software/')[1].split('.html')[0]
		web_apk_url = "http://shouji.baidu.com/software/%s.html" % web_element
		r_2 = requests.get(web_apk_url)
		content_2 = r_2.content.decode("utf-8")
		tree_2 = lxml.html.fromstring(content_2)
		web_apk_data = tree_2.xpath("/html/body/div[2]/div[2]/div/div/div/div[4]/a/@href")[0]
		data = [app_name, web_package_name, web_version, web_apk_data]
		return data

def download_data(data):
	web_data = data
	package_name = data[1] + "-1.apk"
	data_url = data[3]
	r = requests.get(data_url, stream=True, timeout=60)
	print ("start Downloading " + package_name + " ...")
	with open(os.getcwd() + os.path.sep + "Apps" + os.path.sep + package_name, 'wb' ) as fb :
		count = 0
		for chunk in r.iter_content(1024):
			count = count + len(chunk)
			dSize = 0
			dSizeType = ''
			fb.write(chunk) # write bits to file
			if count >= 1024 and count < 1024 * 1024:
				dSize = round(count / float(1024), 2)
				dSizeType = 'KB'
			elif count >= 1024 * 1024:
				dSize = round(count / float(1024 * 1024), 2)
				dSizeType = 'MB'
			else:
				dSize = count
				dSizeType = 'bit'
			print ("Downloaded " + package_name + " " + repr(dSize) + " " + dSizeType, end="\r")
			sys.stdout.flush()
		print ("Downloaded " + package_name + " " + repr(dSize) + " " + dSizeType)
		return 0

if __name__== "__main__":
	web_info_file = open('web_info.csv', 'w+')
	writer = csv.writer(web_info_file)
	writer.writerow(["app_name", "package_name", "wersion", "apk_data"])
	appList = os.getcwd() + os.path.sep + "list.txt"
	for line in open(appList, 'r'):
		try:
			app_name = line.split('\n')[0]
			url = "http://shouji.baidu.com/s?wd=%s" % app_name
			data = get_web_info(app_name, url)
			writer.writerow(data)
			download_data(data)
		except IndexError as e:
			data = [app_name, 'null', 'null', 'null']
			writer.writerow(data)
		finally:
			pass
