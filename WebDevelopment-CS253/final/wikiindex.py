from login import LoginHandler
from login import LogoutHandler
from login import Welcome
from signup import SignUp
from wiki import WikiLoad
from wiki import WikiEdit
from wiki import WikiHistory

UrlHandlers = [("/wiki/signup",SignUp),
				("/wiki/welcome",Welcome),
				("/wiki/login",LoginHandler),
				("/wiki/logout",LogoutHandler),
				("/wiki/*([a-zA-Z0-9_-]*)",WikiLoad),
				("/wiki/_edit/*([a-zA-Z0-9_-]*)",WikiEdit),
				("/wiki/_history/*([a-zA-Z0-9_-]*)",WikiHistory)]