import webapp2
import cgi
import re

Rot13formTemp = """
			<form method="post">
				<textarea name="text" style="width:320px; height:240px;">%(result)s</textarea>
				<br>
				<input type="submit" />
			</form>

			"""

SignUpformTemp = """
				<form method="post">
				<P>
					User Name: <input type="text" name="username" value="%(username)s" />
					<span style="color:#FF0000;"><b>%(1)s</b></span>
				</P>
				<P>
					Password: <input type="password" name="password" />
					<span style="color:#FF0000;"><b>%(2)s</b></span>
				</P>
				<P>
					Verify: <input type="password" name="verify" />
					<span style="color:#FF0000;"><b>%(4)s</b></span>
				</P>
				<P>
					Email: <input type="text" name="email" value="%(email)s" />
					<span style="color:#FF0000;"><b>%(8)s</b></span>
				</P>
				<input type="submit" />
			</form>
				"""

def switchChar(c):
	if ord(c) in range(ord("a"),ord("z")+1):
		return chr(ord("a") + (ord(c)-ord("a") + 13) % 26)
	elif ord(c) in range(ord("A"),ord("Z")+1):
		return chr(ord("A") + (ord(c)-ord("A") + 13) % 26)
	else:
		return cgi.escape(c)

def validInput(value,regex_str):
	regexp = re.compile(regex_str)
	return (regexp.match(value) != None) and 1 or 0

class Rot13(webapp2.RequestHandler):
	def get(self):
		self.response.headers["CONTENT-TYPE"] = 'text/html'
		self.response.write(Rot13formTemp % {"result":""})

	def post(self):
		string = self.request.get("text")
		string = "".join([switchChar(c) for c in string])
		self.response.write(Rot13formTemp % {"result":string})

class SignUp(webapp2.RequestHandler):
	def get(self):
		self.response.headers["CONTENT-TYPE"] = "text/html"
		pageMessage = {"1":"",
						"2":"",
						"4":"",
						"8":"",
						"username":"",
						"email":""}
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")
		result = (14 & validInput(username,r"^[a-zA-Z0-9_-]{3,20}$")) & (13 & validInput(password,r"^.{3,20}$")) & (11 & (password == verify and 1 or 0)) & (7 & validInput(email,r"^[\S]+@[\S]+\.[\S]+$"))
		self.response.write(SignUpformTemp % pageMessage)
	def post(self):
		username = self.request.get("username")
		password = self.request.get("password")
		verify = self.request.get("verify")
		email = self.request.get("email")
		pageMessage = {"1":"That's not a valid username.",
						"2":"That wasn't a valid password.",
						"4":"Your passwords didn't match.",
						"8":"That's not a valid email.",
						"username":username,
						"email":email}
		result = (14 | validInput(username,r"^[a-zA-Z0-9_-]{3,20}$")) & (13 | (validInput(password,r"^.{3,20}$") << 1)) & (11 | ((password == verify and 1 or 0) << 2)) & (7 | ((len(email) == 0 and 1 or 0) or validInput(email,r"^[\S]+@[\S]+\.[\S]+$")) << 3)
		if result == 15:
			self.redirect("/unit2/welcome?username=%s" % username)
		else:
			n = 1
			while result > 0:
				if result & 1 > 0:
					pageMessage[str(n)] = ""
				result >>=1
				n *= 2
		self.response.write(SignUpformTemp % pageMessage)
class WelcomeHandler(webapp2.RequestHandler):
			def get(self):
				self.response.write("Welcome, %s" % self.request.get("username"))
				
UrlHandlers = [("/unit2/rot13", Rot13),
				("/unit2/signup",SignUp),
				("/unit2/welcome",WelcomeHandler)]

