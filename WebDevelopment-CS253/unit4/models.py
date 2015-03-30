from google.appengine.ext import db

class User(db.Model):
	UserName = db.StringProperty()
	Password = db.StringProperty()
	RegistedDate = db.DateTimeProperty(auto_now_add=True)