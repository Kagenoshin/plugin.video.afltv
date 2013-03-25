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

def play(href,fmt,autoplay,cb,name):#to do everything to get all videos for that game
	PH = Pagehandler()
	href2 = Pagehandler.opener.open(href+'?fmt='+fmt+'&amp;autoplay='+autoplay+'&amp;cb='+cb).geturl()
	listitem = xbmcgui.ListItem(name)
  	listitem.setInfo('video', {'Title': name, 'Genre': 'Sport'})
	xbmc.Player().play(href2,listitem)