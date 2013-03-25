#
#    AFLTV XBMC Plugin
#    Copyright (C) 2013 Kagenoshin
#
#    AFLTV is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    AFLTV is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with AFLTV.  If not, see <http://www.gnu.org/licenses/>.
#

# main imports
import sys, os, re, urllib2, urllib
import datetime
from Pagehandler import Pagehandler
from bs4 import BeautifulSoup

from utils import urlstring_to_date
import config

try:
	import xbmc, xbmcgui, xbmcplugin, xbmcaddon
except ImportError:
	pass 

def make_list(href):#to do everything to get all videos for that game
	PH = Pagehandler()
	html = Pagehandler.opener.open('http://afltv.afl.com.au'+href).read()
	if(PH.login_needed(html)):
		PH.login() #ok login, but we do nothing else
		html = Pagehandler.opener.open('http://afltv.afl.com.au'+href).read()
		if(PH.login_needed(html)):
			d = xbmcgui.Dialog()
			d.ok('AFLTV Error', 'AFLTV login failed, check your login data.')
			return False



	#now get the rounds from the html string:
	try:
		videos = []
		soup = BeautifulSoup(html)
		available_videos = soup.find('ul',attrs={'class':re.compile("available-videos")})
		if(not available_videos):
			d = xbmcgui.Dialog()
			d.ok('AFLTV Error', "There are no videos available.")
			return False
		#search for all replay videos
		replays = available_videos.find('li', attrs={'class':re.compile("replay")})
		if(replays):
			for li in replays.find_all('li'):
				current_name = None
				current_href = None
				li2 = str(li)
				a = re.findall(r'<a\s+?class="video".*?href="(.*?)">(.*?)</a>',li2, re.I)
				if(len(a) > 0):
					for ia in a:
						current_href = ia[0]
						current_name = ia[1].strip()
						if(current_href and current_name):
							videos.append({'name':current_name, 'href':current_href, 'channel':'video'})
		#search for all highlight videos
		highlights = available_videos.find('li', attrs={'class':re.compile("highlights")})
		if(highlights):
			for li in highlights.find_all('li'):
				current_name = None
				current_href = None
				li2 = str(li)
				a = re.findall(r'<a\s+?class="video".*?href="(.*?)">(.*?)</a>',li2, re.I)
				if(len(a) > 0):
					for ia in a:
						current_href = ia[0]
						current_name = ia[1].strip()
						if(current_href and current_name):
							videos.append({'name':current_name, 'href':current_href, 'channel':'video'})

		if(len(videos) == 0):
			d = xbmcgui.Dialog()
			d.ok('AFLTV Error', "There are no videos available.")
			return False

		__addon__ = xbmcaddon.Addon()

		ok = fill_media_list_replay(videos)
	except:
		# oops print error message
		print "ERROR:"
		ok = False

	if(ok == 0):
		return False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
	#save cookies
	PH.save_cookie()


def fill_media_list_replay(items):
	#dont know if its already ok!!!!!!
	try:
		ok = True
		# enumerate through the list of categories and add the item to the media list

		for i in items:
			#prepare href (some stupid hack)
			href = re.findall(r'(.*?)\?',i['href'],re.I)
			fmt = re.findall(r'fmt=(.*?)(?=&|$)',i['href'],re.I)
			autoplay = re.findall(r'autoplay=(.*?)(?=&|$)',i['href'],re.I)
			cb = re.findall(r'cb=(\d+?)(?=&|$)',i['href'],re.I)

			#get the right thumbnail and name.
			lname = i['name'].lower()
			if("q1" in lname):
				icon = "nabcup_q1.jpg"
				if(lname == "q1"):
					i['name'] = '1st Quarter - Replay'
			elif("q2" in lname):
				icon = "nabcup_q2.jpg"
				if(lname == "q2"):
					i['name'] = '2nd Quarter - Replay'
			elif("q3" in lname):
				icon = "nabcup_q3.jpg"
				if(lname == "q3"):
					i['name'] = '3rd Quarter - Replay'
			elif("q4" in lname):
				icon = "nabcup_q4.jpg"
				if(lname == "q4"):
					i['name'] = '4th Quarter - Replay'
			elif("highlights" in lname):
				icon = "nabcup_highlights.jpg"
			else:
				icon = "defaultfolder.png"

			#again a stupid hack
			if(len(cb) > 0 and len(fmt)>0 and len(autoplay)>0 and len(href)>0):
				url = "%s?channel=%s&href=%s&ifmtt=%s&jautoplay=%s&kcbbb=%s&lname=%s" % (sys.argv[0], i['channel'],href[0],fmt[0],autoplay[0],cb[0],i['name'])
			else:
				d = xbmcgui.Dialog()
				d.ok('AFLTV Error', "Strange links. AFLTV couldn't build the list.")
				return 0

			#thumbnail = get_thumbnail(c.channel)
			
			listitem = xbmcgui.ListItem(i['name'], iconImage=icon)
			#listitem.setInfo('video',{'episode':s.get_num_episodes()})
			# add the item to the media list

			ok = xbmcplugin.addDirectoryItem(
						handle=int(sys.argv[1]), 
						url=url, 
						listitem=listitem, 
						isFolder=True, 
						totalItems=len(items)
					)

			# if user cancels, call raise to exit loop
			if (not ok):
				raise

		#xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		d.ok('AFLTV Error', 'AFLTV encountered an error:', '  %s (%d) - %s' % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ]) )

		# user cancelled dialog or an error occurred
		print "ERROR: %s (%d) - %s" % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
		ok = False

	return ok