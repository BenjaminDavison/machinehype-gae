''' 
	This isn't the nicest code I have ever written, I wrote this in a few hours
	to test out google appengine webapp2 - so everything is squished together
	in one file with very little regards to classes but it does have some niceties,
	also I could not get some of the nosql concepts working in the limited time
	I had to write this app.
	
	Also no pagination or personable likes, I did see a toolkit on github that had a bunch of other
	little nicknacks but that would of been a bit overwhelming for the little time I had 
'''

import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users
import webapp2

import os
from google.appengine.ext.webapp import template

class Song(db.Model):
	mp3_url = db.StringProperty(multiline=False)
	title = db.StringProperty(multiline=False)
	blurb = db.StringProperty(multiline=True)
	site_name = db.StringProperty(multiline=False)
	site_url = db.StringProperty(multiline=False)
	likes = db.IntegerProperty()
	date = db.DateTimeProperty(auto_now_add=True)

def site_key(site_name=None):
	"""Constructs a datastore key for a Guestbook entity with guestbook_name."""
	return db.Key.from_path('Site', site_name or 'default_site')

def RetriveSongs(site_name, filterPopular=False):
	
	if filterPopular == False:
		songs_query = Song.all().ancestor(
										site_key(site_name)).order('-date')
	else:
		songs_query = Song.all().ancestor(
										site_key(site_name)).order('-likes')
	
	return songs_query.fetch(10)

def IsUserLoggedIn(requesturi):
	if users.get_current_user():
		return users.create_logout_url(requesturi), 'Logout'
	else:
		return users.create_login_url(requesturi), 'Login'	

class MainPage(webapp2.RequestHandler):
	def get(self):
		site_name = self.request.get('site_name')
		songs = RetriveSongs(site_name, False)
		url, url_linktext = IsUserLoggedIn(self.request.uri)
		
		template_values = {
			'songs': songs,
			'url': url,
			'url_linktext': url_linktext,
		}
		
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))
			
class AddSong(webapp2.RequestHandler):
	def post(self):
		# We set the same parent key on the 'Greeting' to ensure each greeting is in
		# the same entity group. Queries across the single entity group will be
		# consistent. However, the write rate to a single entity group should
		# be limited to ~1/second.
		site_name = self.request.get('site_name')
		song = Song(parent=site_key(site_name))
	
		if users.get_current_user():

			song.mp3_url = self.request.get('mp3_url')
			song.title = self.request.get('title')
			song.blurb = self.request.get('blurb')
#			song.site_name = self.request.get('site_name')
			song.site_url = self.request.get('site_url')
			song.likes = 0
			
			song.put()
			self.redirect('/?' + urllib.urlencode({'site_name': site_name}))
			
class LikeSong(webapp2.RequestHandler):
	def post(self):
		raw_id = self.request.get('key')
		s = Song.get(self.request.get('key'))
		s.likes += 1
		s.put()
		 
		self.redirect('/')
	
class PopularSongs(webapp2.RequestHandler):
	def get(self):
		site_name = self.request.get('site_name')
		songs = RetriveSongs(site_name, True)
		url, url_linktext = IsUserLoggedIn(self.request.uri)
		
		template_values = {
			'songs': songs,
			'url': url,
			'url_linktext': url_linktext,
		}
		
		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))
		
		
application = webapp2.WSGIApplication([
	('/', MainPage),
	('/addsong', AddSong),
	('/likesong', LikeSong),
	('/popular_songs', PopularSongs),
], debug=True)

def main():
	application.run()

if __name__ == '__main__':
	main()
