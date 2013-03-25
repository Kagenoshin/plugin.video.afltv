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

try:
	import xbmc, xbmcgui, xbmcplugin, xbmcaddon
except ImportError:
	pass 

def make_list():#to do everything to get all the rounds
	datenow = datetime.date.today()

	PH = Pagehandler()
	html = Pagehandler.opener.open('http://afltv.afl.com.au/schedule/group_view').read()
	if(PH.login_needed(html)):
		PH.login() #ok login, but we do nothing else

	#now get the rounds from the html string:
	try:
		rounds = []
		soup = BeautifulSoup(html)
		for r in soup.find_all('li', attrs={"class":"linked round"}):
			ra = r.find('a')
			ras = ra.find('span')
			dateround = urlstring_to_date(str(ra['href']))
			if(dateround):
				#we want to display only rounds which are not in the future
				ddiff = dateround-datenow
				diff = ddiff.days
				if(diff <= 1): #because of different timezones it could be an other day.
					rounds.append({'name':str(ras.text),'href':str(ra['href']),'channel':'rounds'})

		__addon__ = xbmcaddon.Addon()

		ok = fill_media_list_replay(rounds)
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