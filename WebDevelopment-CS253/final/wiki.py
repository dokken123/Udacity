import webapp2
from baseHandler import renderTemplate
from utils import getUser
from model import Wiki
from google.appengine.api import memcache

def getWikiFromCache(wikititle,update=False,getHistory=False):
	wikis = memcache.get(wikititle)
	if wikis == None or update:
		wikis = Wiki.gql("WHERE title=:1 ORDER BY created DESC",wikititle).fetch(None)
		memcache.set(wikititle,wikis)
	if getHistory:
		return wikis
	else:
		return wikis and wikis[0] or None

class WikiLoad(webapp2.RequestHandler):
	def get(self,wikititle=None):
		wiki = getWikiFromCache(wikititle)
		if wiki:
			user = getUser(self.request.cookies.get("user"))
			self.response.write(renderTemplate("templates/final/wikiIndex.html",{"wiki":wiki,"user":user}))
		else:
			self.redirect("/wiki/_edit/%s" % wikititle)
		
class WikiEdit(webapp2.RequestHandler):
	def get(self,wikititle=None):
		user = getUser(self.request.cookies.get("user"))
		if user:
			wiki = getWikiFromCache(wikititle)
			if wiki == None:
				wiki = Wiki(title=wikititle,content="")
			self.response.write(renderTemplate("templates/final/wikiedit.html",{"wiki":wiki,"user":user}))
		else:
			self.redirect("/wiki/login")
	def post(self,wikititle=None):
		user = getUser(self.request.cookies.get("user"))
		if user:
			wikicontent = self.request.get("content").replace("\n","<br/>")
			wiki = Wiki(title=wikititle,content=wikicontent,author=user)
			if len(wikicontent) == 0:
				self.response.write(renderTemplate("templates/final/wikiedit.html",{"wiki":wiki,"user":user,"errormsg":"Please input content!"}))
			else:
				wiki.put()
				getWikiFromCache(wikititle,True)
				self.redirect("/wiki/%s" % wikititle)
		else:
			self.redirect("/wiki/login")

class WikiHistory(webapp2.RequestHandler):
	def get(self,wikititle=None):
		wikiHistory = getWikiFromCache(wikititle,False,True)
		self.response.write(renderTemplate("templates/final/wikihistory.html",{"wikis":wikiHistory,"wikititle":wikititle}))
		