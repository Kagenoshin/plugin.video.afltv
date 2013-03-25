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
import sys, os, urllib2, urllib
import datetime
from Pagehandler import Pagehandler
from bs4 import BeautifulSoup

from utils import urlstring_to_date
import config

try:
	import xbmc, xbmcgui, xbmcplugin, xbmcaddon
except ImportError:
	pass 

def make_list(href):#to do everything to get all games in that round

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
		games = []
		soup = BeautifulSoup(html)
		Roundname = soup.find('h3').text
		while(True):
			if(soup.find('h3').text != Roundname):
				break
			videolist = soup.find('div', attrs={'id':"fixture-list"})
			if(not videolist):
				d = xbmcgui.Dialog()
				d.ok('AFLTV Error', 'AFLTV something went wrong, cant buid list.')
				soup = get_next_page(soup) #we look for the next page
				if(not soup): #there is no next page
					break
				elif(soup == 0): #there was a login error exit
					return False
				else:
					continue #continue with the next page

			for listelement in videolist.find_all('div', attrs={"data-event-id":True}):
				link = None
				current_team_home = None
				current_team_guest = None
				if(len(listelement.find_all('a', attrs={'class':'video'})) > 0): #we have some videos, if not ignore it!
					teams = listelement.find('ul', attrs={'class':'teams'})
					if(not teams):
						continue
					for li in teams.find_all('li'):
						clases = li['class']
						for c in clases:
							if('first' == str(c)):
								current_team_home = str(li.text).strip()
								current_team_home = current_team_home.lower()
							elif('last' == str(c)):
								current_team_guest = str(li.text).strip()
								current_team_guest = current_team_guest.lower()

					videos = listelement.find('ul', attrs = {'class':"video-details"})
					if(not videos):
						continue
					for li in videos.find_all('li'):
						lstr = str(li).lower() 
						if("replay" in lstr or "highlights" in lstr):
							try:
								link = str(li.find('a')['href'])
								break
							except:
								continue

					if(link and current_team_home and current_team_guest):
						games.append({'name':config.TEAMS[current_team_home]+" vs "+config.TEAMS[current_team_guest], 'href':link, 'channel':'game'})

			#get the next page (if there is one)
			next = soup.find('li', attrs={'class':'next'})
			if(not next):
				break
			else:
				try:
					anext = next.find('a', attrs={"href":True})
					if(not anext):
						break
					nexthref = str(anext['href'])
					html = Pagehandler.opener.open('http://afltv.afl.com.au'+nexthref).read()
					if(PH.login_needed(html)):
						PH.login() #ok login, but we do nothing else
						html = Pagehandler.opener.open('http://afltv.afl.com.au'+nexthref).read()
						if(PH.login_needed(html)):
							d = xbmcgui.Dialog()
							d.ok('AFLTV Error', 'AFLTV login failed, check your login data.')
							return False
					soup = BeautifulSoup(html)
				except:
					break
		if(len(games) == 0):
			d = xbmcgui.Dialog()
			d.ok('AFLTV Error', "There are no games available.")
			return False

		__addon__ = xbmcaddon.Addon()

		ok = fill_media_list_replay(games)
	except:
		# oops print error message
		print "ERROR:"
		ok = False

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
			url = "%s?channel=%s&href=%s" % (sys.argv[0], i['channel'],i['href'])
			#thumbnail = get_thumbnail(c.channel)
			icon = "defaultfolder.png"
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

def get_next_page(soup):
	#get the next page (if there is one)
	next = soup.find('li', attrs={'class':'next'})
	if(not next):
		return None
	else:
		try:
			anext = next.find('a', attrs={"href":True})
			if(not anext):
				return None
			nexthref = str(anext['href'])
			html = Pagehandler.opener.open('http://afltv.afl.com.au'+nexthref).read()
			if(PH.login_needed(html)):
				PH.login() #ok login, but we do nothing else
				html = Pagehandler.opener.open('http://afltv.afl.com.au'+nexthref).read()
				if(PH.login_needed(html)):
					d = xbmcgui.Dialog()
					d.ok('AFLTV Error', 'AFLTV login failed, check your login data.')
					return 0
			soup = BeautifulSoup(html)
			return soup
		except:
			return None