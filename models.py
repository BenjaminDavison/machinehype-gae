from google.appengine.ext import db
from google.appengine.api import users
import webapp2
from ndb import key, model

#models
class Site(db.Model):
    name = db.StringProperty(multiline=False)    
    site_url = db.StringProperty(multiline=False)

class Song(db.Model):
    mp3_url = db.StringProperty(multiline=False)
    title = db.StringProperty(multiline=False)
    likes = db.IntegerProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    site_name = db.StringProperty(multiline=False)
    site = db.ReferenceProperty(Site,
                                collection_name="songs")

class UserPrefs(db.Model):
    user = db.UserProperty()
    songs = db.ListProperty(db.Key)