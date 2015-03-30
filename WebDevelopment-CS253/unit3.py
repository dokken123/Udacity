import webapp2

import baseHandler
import datavisitor

from datavisitor import Blog
from baseHandler import renderTemplate

blog_form_template = """
					<form action="/unit3/blog/newpost" method="POST">
						<label>Subject:
							<P>
								<input type="text" name="subject" style="width:300px" value="%(subject)s" />
								<span style="color:#FF0000">
									%(subjecterror)s
								</span>
							</P>
						</label>
						<BR>
						<label>Content:
							<P>
								<textarea name="content" style="width:300px;height:200px">%(content)s</textarea>
								<span style="color:#FF0000">
									%(contenterror)s
								</span>
							</P>
						</label>
						<input type="submit" />
					</form>
					"""

class Blogs(webapp2.RequestHandler):
	def get(self,blog_id=None):
		if blog_id:
			blogs = [Blog.get_by_id(int(blog_id))]
		else:
			blogs = datavisitor.GetAllData("Blog")
		self.response.write(renderTemplate("templates/unit3/blogs.html",{"blogs":blogs}))

class PostBlog(webapp2.RequestHandler):
	def get(self):
		formcontent = {"subjecterror": "", "contenterror":"","subject":"","content":""}
		self.response.write(blog_form_template % formcontent)

	def post(self):
		subject = self.request.get("subject")
		content = self.request.get("content")
		if len(subject) > 0 and len(content) > 0:
			dataModel = Blog(subject=subject,content=content)
			datavisitor.PutModel(dataModel)
			self.redirect("/unit3/blog/%s" % dataModel.key().id())
		else:
			formcontent = {"subjecterror": "", "contenterror":"","subject":subject,"content":content}
			if len(subject) == 0:
				formcontent["subjecterror"] = "Please input subject!"
			if len(content) == 0:
				formcontent["contenterror"] = "Please input content!"
			self.response.write(blog_form_template % formcontent)

UrlHandlers = [("/unit3/blog/*([\d]*)",Blogs),("/unit3/blog/newpost",PostBlog)]
		
