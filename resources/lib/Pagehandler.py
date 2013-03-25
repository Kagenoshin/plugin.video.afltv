#!/usr/bin/python
# -*- coding: latin-1 -*-

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

import urllib,urllib2,re, cookielib
import xbmcgui, xbmcplugin, xbmcaddon, xbmc


class Pagehandler(object):
	opener = None
	cj = None
	basic_url = 'http://afltv.afl.com.au/'
	cookiefile = '/cookie/cookiefile.lwp'

	def __init__(self):
		if(not Pagehandler.opener):
			__addon__ = xbmcaddon.Addon()
			path = __addon__.getAddonInfo('path').decode('utf-8')
			Pagehandler.cookiefile = path + Pagehandler.cookiefile
			Pagehandler.cookiefile = xbmc.translatePath(Pagehandler.cookiefile)
			Pagehandler.cj = cookielib.LWPCookieJar(Pagehandler.cookiefile)
			Pagehandler.cj.load(Pagehandler.cookiefile)
			Pagehandler.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(Pagehandler.cj))
			Pagehandler.opener.addheaders = [('User-agent', 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3')]
			Pagehandler.opener.open(Pagehandler.basic_url)

	def login_needed(self, html):
		if( '<li class="nav-logout-account" id="nav-logout"><a href="https://afltv.afl.com.au/auth/logout"  title="Log Out">Log Out</a></li>' not in html or '<li class="nav-login-register" id="nav-login"><a class="trigger" href="#"><span>Log In</span></a>' in html):
			return True
		else:
			return False

	def login(self):
		__addon__ = xbmcaddon.Addon()
		username =  __addon__.getSetting('USERNAME')
		password =  __addon__.getSetting('PASSWORD')
		data = {'identity':username,'password':password,'remember':1}
		dat = urllib.urlencode(data)
		resp = Pagehandler.opener.open('https://afltv.afl.com.au/auth/login', dat)

	def save_cookie(self):
		Pagehandler.cj.save(Pagehandler.cookiefile)
