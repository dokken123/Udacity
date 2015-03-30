import webapp2
from baseHandler import validInput
from baseHandler import renderTemplate
from utils import hash_str
from utils import getUser
from model import User

class LoginHandler(webapp2.RequestHandler):
	def get(self):
		pageMessage = {"error1":"",
						"error2":"",
						"loginfailed":"",
						"username":""}
		self.response.write(renderTemplate("templates/final/login.html",pageMessage))

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
				self.response.headers.add_header("Set-Cookie","user=%s;Path=/wiki/" % str(hash_str(user.key().id())))
				self.redirect("welcome")
			else:
				pageMessage["error1"] = ""
				pageMessage["error2"] = ""
				pageMessage["loginfailed"] = "Non-existed user!"
				self.response.write(renderTemplate("templates/final/login.html",pageMessage))
		else:
			n = 1
			while result > 0:
				if result & 1 > 0:
					pageMessage["error%s" % n] = ""
				result >>= 1
				n *= 2
			self.response.write(renderTemplate("templates/final/login.html",pageMessage))

class LogoutHandler(webapp2.RequestHandler):
	def get(self):
		self.response.headers.add_header("Set-Cookie","user=;Path=/wiki/")
		self.redirect("signup")

class Welcome(webapp2.RequestHandler):
	def get(self):
		user = getUser(self.request.cookies.get("user"))
		if user:
			self.redirect("/wiki/")
		else:
			#raise Exception("Cookie hacking detected!")
			self.redirect("signup")