from google.appengine.ext import db

class Blog(db.Model):
	subject = db.StringProperty()
	content = db.TextProperty()
	created = db.DateTimeProperty(auto_now_add=True)

def PutModel(dbmodel):
	dbmodel.put()

def GetAllData(tableName):
	return db.GqlQuery("SELECT * FROM %s" % tableName)