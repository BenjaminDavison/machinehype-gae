''' 
    A parser I wrote for another project that has been reused for this machine hype project.
    
    This has a few problems as a parser is one of those projects with a million edge cases,
    it will currently go through the rss feeds correctly and will try and extract *something*
    out of the feed but annoyingly it sometimes the feed will come out in some really stupid
    title naming scheme where it seems they have  titles duplicated, another note is because
    this parser was written for another application a while back it is decoupled from djangos
    models so it just slaps the raw sql straight into the DB.
'''
import feedparser
from future import Future
import MySQLdb
import bleach
import datetime
from HTMLParser import HTMLParser

#stuff to clean the database input
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

class rssparser():
    #the mysqldb cursor
    cursor = None
    
    html_escape_table = {
        "&": "",
        '"': "",
        "'": "",
        ">": "",
        "<": "",
        }
    
    def __init__(self):
        #setup database connection
        conn = MySQLdb.connect('localhost', 'root', 
        '', 'django', use_unicode=True);
        #innodb funny buisness
        conn.autocommit(True)
        conn.set_character_set('utf8')
        
        #http://www.dasprids.de/blog/2007/12/17/python-mysqldb-and-utf-8
        self.cursor = conn.cursor (MySQLdb.cursors.DictCursor)
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')
        
    #cleaning up the stuff we get back from the feed
    def html_escape(self, text):
        """Produce entities within text."""
        return "".join(self.html_escape_table.get(c,c) for c in text)
    
    #cleaning up the stuff we get back from the feed
    def strip_tags(self, html):
        s = MLStripper()
        s.feed(html)
        return self.html_escape(s.get_data())
    
    #if we want to return a dictionary from a mysql query
    def mysql_return(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    #the meat of parsing
    def parsefeeds(self):
        #grab all the sites from teh django application
        query = "SELECT rss_url, id, last_crawled FROM hype_site"
        result_set = self.mysql_return(query)

        hit_list = [] # list of feeds to pull down
        for rssUrl in result_set[:]:
            feed = feedparser.parse(rssUrl['rss_url'], rssUrl['last_crawled'])
            
            entries = []
            entries.extend( feed[ "items" ] )
            
            #grab links
            for entry in entries[:]:
                #do we have an mp3 in the links?
                for link in entry['links'][:]:
                    if '.mp3' in link['href']:
                        now = datetime.datetime.now()
                        
                        #bung this into the DB
                        query = """INSERT INTO hype_song (name, artist, blurb, pub_date, mp3_url, likes, site_id) 
                                            VALUES ('%s', '%s', '%s', '%s 00:00:00', '%s', 0, '%s')""" % (self.strip_tags(entry['title']),
                                                                                                       self.strip_tags(entry['title']),
                                                                                                       self.strip_tags(entry['content'][0]['value'][:256]),
                                                                                                       now, link['href'], rssUrl['id'])
                        
                        #this isn't the nicest way to handle this, but the scope of this means if we miss one
                        #or two songs it does not really matter all that much
                        try:
                            self.cursor.execute(query)
                        except:
                            print "Inserting into the DB failed with query: %s" % (query)
                        
            #need to tell the site model when the rss feed got last scraped
            query = 'UPDATE hype_site SET last_crawled=\'%s\' WHERE id=%d' % (datetime.datetime.now(), rssUrl['id'])
            self.cursor.execute(query)
                        


rp = rssparser()

rp.parsefeeds()