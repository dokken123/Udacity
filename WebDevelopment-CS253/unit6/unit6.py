import webapp2
import json
import hmac
import hashlib
import datavisitor
import time

from baseHandler import renderTemplate
from baseHandler import validInput
from models import Blog
from models import User
from cgi import escape
from google.appengine.api import memcache

blog_form_template = """
					<form action="/unit6/newpost" method="POST">
						<label>Subject:
							<P>
								<input type="text" name="subject" style="width:300px" value="%(subject)s" />
								<span style="color:#FF0000">
									%(subjecterror)s
								</span>
							</P>
						</label>
						<BR>
						<label>Content:
							<P>
								<textarea name="content" style="width:300px;height:200px">%(content)s</textarea>
								<span style="color:#FF0000">
									%(contenterror)s
								</span>
							</P>
						</label>
						<input type="submit" />
					</form>
					"""

hashKey = "imasecret"

cacheKey = "BLOGS"
lastCacheTime = time.time()

def hash_str(info):
	info = str(info)
	return "%s|%s" % (info,hmac.new(hashKey,info,hashlib.sha256).hexdigest())

def checkHash(hashstr):
	return hashstr == hash_str(hashstr.split("|")[0])

def getUser(usrCookie):
	userId = usrCookie
	if userId and checkHash(userId):
		userId = int(userId.split("|")[0])
		user = User.get_by_id(userId)
		return user
	else:
		return None

def getBlogCache():
	val = memcache.get(cacheKey)
	return val

def setBlogCache(blogs):
	memcache.set(cacheKey,blogs)

def retrieveBlogs(blog_id=None,update=False):
	blogs = getBlogCache()
	global lastCacheTime
	if update or blogs==None:
		blogs = datavisitor.GetAllData("Blog")
		if len([b for b in blogs]) > 0:
			setBlogCache(blogs)
			lastCacheTime = time.time()
	if blog_id:
		return [b for b in blogs if str(b.key().id()) == blog_id]
	else:
		return blogs
		

class Blogs(webapp2.RequestHandler):
	def get(self,blog_id=None,isJson=None):
		blogs = retrieveBlogs(blog_id)
		if not isJson:
			self.response.write(renderTemplate("templates/unit6/blogs.html",{"blogs":blogs,"last_cache":lastCacheTime and int(time.time() - lastCacheTime) or "0"}))
		else:
			self.response.headers["Content-Type"] = "application/json"
			self.response.write(json.dumps([{"subject":escape(b.subject),"content":escape(b.content),"author":b.author and {"id":b.author.key().id(),"UserName":b.author.UserName} or None} for b in blogs]))

class BlogJSONHandler(webapp2.RequestHandler):
	def get(self,blog_id=None):
		self.response.write("JSON")
				

class PostBlog(webapp2.RequestHandler):
	def get(self):
		user = getUser(self.request.cookies.get("user"))
		if user:
			formcontent = {"subjecterror": "", "contenterror":"","subject":"","content":""}
			self.response.write(blog_form_template % formcontent)
		else:
			self.redirect("login")

	def post(self):
		user = getUser(self.request.cookies.get("user"))
		if user:
			subject = self.request.get("subject")
			content = self.request.get("content")
			if len(subject) > 0 and len(content) > 0:
				content = escape(content).replace("\n","<br/>")
				dataModel = Blog(subject=escape(subject),content=content,author=user)
				datavisitor.PutModel(dataModel)
				retrieveBlogs(update=True)
				self.redirect("/unit6/%s" % dataModel.key().id())
			else:
				formcontent = {"subjecterror": "", "contenterror":"","subject":subject,"content":content}
				if len(subject) == 0:
					formcontent["subjecterror"] = "Please input subject!"
				if len(content) == 0:
					formcontent["contenterror"] = "Please input content!"
				self.response.write(blog_form_template % formcontent)
		else:
			self.redirect("login")


class SignUp(webapp2.RequestHandler):
	def get(self):
		pageMessage = {"error1":"",
						"error2":"",
						"error4":"",
						"error8":"",
						"username":"",
						"email":""}
		self.response.write(renderTemplate("templates/unit6/signup.html",pageMessage))
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")
		pageMessage = {"error1":"That's not a valid username.",
						"error2":"That wasn't a valid password.",
						"error4":"Your passwords didn't match.",
						"error8":"That's not a valid email.",
						"username":username,
						"email":email}
		result = (14 | validInput(username,r"^[a-zA-Z0-9_-]{3,20}$")) & (13 | (validInput(password,r"^.{3,20}$") << 1)) & (11 | ((password == verify and 1 or 0) << 2)) & (7 | ((len(email) == 0 and 1 or 0) or validInput(email,r"^[\S]+@[\S]+\.[\S]+$")) << 3)
		if result == 15:
			hashedPass = hash_str("%s%s" % (username,password)).split("|")[1]
			user = User(UserName=username,Password=hashedPass)
			user.put()
			self.response.headers.add_header("Set-Cookie","user=%s;Path=/unit6/" % str(hash_str(user.key().id())))
			self.redirect("/unit6/welcome")
		else:
			n = 1
			while result > 0:
				if result & 1 > 0:
					pageMessage["error%s" % n] = ""
				result >>=1
				n *= 2
		self.response.write(renderTemplate("templates/unit6/signup.html",pageMessage))

class LoginHandler(webapp2.RequestHandler):
	def get(self):
		pageMessage = {"error1":"",
						"error2":"",
						"loginfailed":"",
						"username":""}
		self.response.write(renderTemplate("templates/unit6/login.html",pageMessage))

	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		pageMessage = {"error1":"That's not a valid username.",
						"error2":"That wasn't a valid password.",
						"loginfailed":"",
						"username":username}
		result = (2 | validInput(username,r"^[a-zA-Z0-9_-]{3,20}$")) & (1 | validInput(password,r"^.{3,20}$") << 1)
		if result == 3:
			hashedPass = hash_str("%s%s" % (username,password)).split("|")[1]
			userCursor = User.gql("WHERE UserName=:1 AND Password=:2",username,hashedPass)
			user = userCursor.get()
			if user:
				self.response.headers.add_header("Set-Cookie","user=%s;Path=/unit6/" % str(hash_str(user.key().id())))
				self.redirect("/unit6/welcome")
			else:
				pageMessage["error1"] = ""
				pageMessage["error2"] = ""
				pageMessage["loginfailed"] = "Non-existed user!"
				self.response.write(renderTemplate("templates/unit6/login.html",pageMessage))
		else:
			n = 1
			while result > 0:
				if result & 1 > 0:
					pageMessage["error%s" % n] = ""
				result >>= 1
				n *= 2
			self.response.write(renderTemplate("templates/unit6/login.html",pageMessage))

class LogoutHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers.add_header("Set-Cookie","user=;Path=/unit6/")
		self.redirect("signup")
		

class FlushCacheHandler(webapp2.RequestHandler):
	def get(self):
		memcache.flush_all()
		self.redirect("/unit6/")
		

class Welcome(webapp2.RequestHandler):
	def get(self):
		user = getUser(self.request.cookies.get("user"))
		if user:
			self.response.write("Welcome, %s" % user.UserName)
		else:
			#raise Exception("Cookie hacking detected!")
			self.redirect("signup")

UrlHandlers = [("/unit6/*([\d]*)/*(\.json)*",Blogs),
				("/unit6/newpost",PostBlog),
				("/unit6/flush",FlushCacheHandler),
				("/unit6/signup",SignUp),
				("/unit6/welcome",Welcome),
				("/unit6/login",LoginHandler),
				("/unit6/logout",LogoutHandler)]
		
