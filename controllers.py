import cgi
import datetime
import urllib
import wsgiref.handlers
import webapp2
import os
from ndb import key, model
from google.appengine.ext.webapp import template
from webapp2_extras.appengine.auth.models import User
from google.appengine.api import users

from models import Site, Song, UserPrefs

def RetriveSongsBySite(site_name):    
    if site_name == '':
        site = Site.all().fetch(150)
    else:
        site = Site.all().filter('name =', site_name).fetch(1)
        
    return site

def RetrivePopularSongs():
    songs_query = Song.all().order('-likes')
        
    #until pagination
    return songs_query.fetch(10)

def IsUserLoggedIn(requesturi):
    if users.get_current_user():
        return users.create_logout_url(requesturi), 'Logout'
    else:
        return users.create_login_url(requesturi), 'Login'
    

def GetDistinctKey(model, args):
    unique_results = []    
    array = model.all()
    
    for obj in array:
        if getattr(obj, args) not in unique_results:
            unique_results.append(obj)
            
    return unique_results
   
def GetDistinctTopLevelModel(model):
    return set(model.all())

class MainPage(webapp2.RequestHandler):
    def get(self):
        site_name = self.request.get('site_name')
        sites = RetriveSongsBySite(site_name)
        url, url_linktext = IsUserLoggedIn(self.request.uri)
        
        songs = []
        
        for site in sites[:]:
            songs.extend(site.songs)

        template_values = {
            'songs': songs,
            'url': url,
            'url_linktext': url_linktext,
        }
        
        user1 = users.get_current_user()
        
        UserPrefs(user=user1).put()
        

#            pass
##            property = s.get().property

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        

        
        
class SiteList(webapp2.RequestHandler):
    def get(self):
        sites = GetDistinctKey(Site, 'name')
        url, url_linktext = IsUserLoggedIn(self.request.uri)
        
        a = Site.all().filter('site_name =', 'sdfsdf')
        results = a.fetch(limit=5)
        
        template_values = {
            'sites': sites,
            'url': url,
            'url_linktext': url_linktext,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'sites.html')
        self.response.out.write(template.render(path, template_values))
            
class AddSong(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'addsong.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        site_name = self.request.get('site_name')
        
        #this is dodgy, I would rather do something like Site.get(name=site_name) but I can't get that
        #to work...
        p = Site.all().filter('name =', site_name).fetch(1)
        
        if users.get_current_user():
            Song(site = p[0],
                 title = self.request.get('title'),
                 mp3_url = self.request.get('mp3_url'),
                 likes = 0).put()
                 
            self.redirect('/?' + urllib.urlencode({'site_name': p[0].name}))
            
class AddSite(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'addsite.html')
        self.response.out.write(template.render(path, template_values))
    def post(self):
        if users.get_current_user():
            Site(name = self.request.get('name'),
                 site_url = self.request.get('site_url')).put()
                 
        self.redirect('/')
        
            
class LikeSong(webapp2.RequestHandler):
    def post(self):
        s = Song.get(self.request.get('key'))
        s.likes += 1
        s.put()
        
        user = users.get_current_user()
        friends = s
        mary = UserPrefs.all().filter('user =', user).fetch(1)

        if friends.key() not in mary[0].songs:
            mary[0].songs.append(friends.key())
            mary[0].put()
         
        self.redirect('/')

class UserSongs(webapp2.RequestHandler):
    def get(self):
        site_name = self.request.get('user')
        url, url_linktext = IsUserLoggedIn(self.request.uri)
        
        user = users.get_current_user()
        songList = UserPrefs.all().filter('user =', user).fetch(1)
        
        #janky
#        print songList[0].songs[1]
        songs = []
        for s in songList[:]:
            for k in s.songs[:]:
                songs.append(Song.get(k))
        
        template_values = {
            'songs': songs,
            'url': url,
            'url_linktext': url_linktext,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'usersongs.html')
        self.response.out.write(template.render(path, template_values))
            
class PopularSongs(webapp2.RequestHandler):
    def get(self):
        site_name = self.request.get('site_name')
        songs = RetrivePopularSongs()
        url, url_linktext = IsUserLoggedIn(self.request.uri)
        
        template_values = {
            'songs': songs,
            'url': url,
            'url_linktext': url_linktext,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'popular.html')
        self.response.out.write(template.render(path, template_values))