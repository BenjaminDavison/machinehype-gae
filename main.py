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
import webapp2
import os

from google.appengine.ext import db
from google.appengine.api import users
from ndb import key, model
from google.appengine.ext.webapp import template
from webapp2_extras.appengine.auth.models import User
from controllers import MainPage, SiteList, AddSong, AddSite, LikeSong, PopularSongs, UserSongs

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sitelist', SiteList),
    ('/addsong', AddSong),
    ('/addsite', AddSite),
    ('/likesong', LikeSong),
    ('/popular_songs', PopularSongs),
    ('/usersongs', UserSongs),
], debug=True)

def main():
    application.run()

if __name__ == '__main__':
    main()
