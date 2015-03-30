from google.appengine.ext import db

class User(db.Model):
	UserName = db.StringProperty()
	Password = db.StringProperty()
	RegistedDate = db.DateTimeProperty(auto_now_add=True)

class Wiki(db.Model):
	title = db.StringProperty()
	content = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add=True)
	author = db.ReferenceProperty(User)