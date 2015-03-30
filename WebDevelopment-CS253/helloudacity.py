import webapp2
import unit2
import unit3
from unit4 import unit4
from unit5 import unit5
from unit6 import unit6
from final import wikiindex

handlers = []
handlers.extend(unit2.UrlHandlers)
handlers.extend(unit3.UrlHandlers)
handlers.extend(unit4.UrlHandlers)
handlers.extend(unit5.UrlHandlers)
handlers.extend(unit6.UrlHandlers)
handlers.extend(wikiindex.UrlHandlers)
app = webapp2.WSGIApplication(handlers,debug=True)
