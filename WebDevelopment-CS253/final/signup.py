import webapp2
from baseHandler import validInput
from baseHandler import renderTemplate
from utils import hash_str
from utils import getUser
from model import User

class SignUp(webapp2.RequestHandler):
	def get(self):
		pageMessage = {"error1":"",
						"error2":"",
						"error4":"",
						"error8":"",
						"username":"",
						"email":""}
		self.response.write(renderTemplate("templates/final/signup.html",pageMessage))
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
			self.response.headers.add_header("Set-Cookie","user=%s;Path=/wiki/" % str(hash_str(user.key().id())))
			self.redirect("welcome")
		else:
			n = 1
			while result > 0:
				if result & 1 > 0:
					pageMessage["error%s" % n] = ""
				result >>=1
				n *= 2
			self.response.write(renderTemplate("templates/final/signup.html",pageMessage))
