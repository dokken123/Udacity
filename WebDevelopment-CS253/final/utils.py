import hmac
import hashlib

from model import User

hashKey = "imasecret"

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