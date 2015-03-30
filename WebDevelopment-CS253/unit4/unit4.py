import webapp2
import hmac
import hashlib

from baseHandler import renderTemplate
from baseHandler import validInput

from models import User

hashKey = "imasecret"

def hash_str(info):
	info = str(info)
	return "%s|%s" % (info,hmac.new(hashKey,info,hashlib.sha256).hexdigest())

def checkHash(hashstr):
	return hashstr == hash_str(hashstr.split("|")[0])

class SignUp(webapp2.RequestHandler):
	def get(self):
		pageMessage = {"error1":"",
						"error2":"",
						"error4":"",
						"error8":"",
						"username":"",
						"email":""}
		self.response.write(renderTemplate("templates/unit4/signup.html",pageMessage))
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
			self.response.headers.add_header("Set-Cookie","user=%s;Path=/unit4/" % str(hash_str(user.key().id())))
			self.redirect("/unit4/welcome")
		else:
			n = 1
			while result > 0:
				if result & 1 > 0:
					pageMessage["error%s" % n] = ""
				result >>=1
				n *= 2
		self.response.write(renderTemplate("templates/unit4/signup.html",pageMessage))

class LoginHandler(webapp2.RequestHandler):
	def get(self):
		pageMessage = {"error1":"",
						"error2":"",
						"loginfailed":"",
						"username":""}
		self.response.write(renderTemplate("templates/unit4/login.html",pageMessage))

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
				self.response.headers.add_header("Set-Cookie","user=%s;Path=/unit4/" % str(hash_str(user.key().id())))
				self.redirect("/unit4/welcome")
			else:
				pageMessage["error1"] = ""
				pageMessage["error2"] = ""
				pageMessage["loginfailed"] = "Non-existed user!"
				self.response.write(renderTemplate("templates/unit4/login.html",pageMessage))
		else:
			n = 1
			while result > 0:
				if result & 1 > 0:
					pageMessage["error%s" % n] = ""
				result >>= 1
				n *= 2
			self.response.write(renderTemplate("templates/unit4/login.html",pageMessage))

class LogoutHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers.add_header("Set-Cookie","user=;Path=/unit4/")
		self.redirect("signup")
		

class Welcome(webapp2.RequestHandler):
	def get(self):
		userId = self.request.cookies.get("user")
		if checkHash(userId):
			userId = int(userId.split("|")[0])
			user = User.get_by_id(userId)
			self.response.write("Welcome, %s" % user.UserName)
		else:
			#raise Exception("Cookie hacking detected!")
			self.redirect("/unit4/signup")

UrlHandlers = [("/unit4/signup",SignUp),
				("/unit4/welcome",Welcome),
				("/unit4/login",LoginHandler),
				("/unit4/logout",LogoutHandler)]

