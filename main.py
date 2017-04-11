import webapp2
import os
import jinja2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

# allows you to use databases with GAE
from google.appengine.ext import db

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    blog_title = db.StringProperty(required = True)
    blog_body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainHandler(Handler):
    def render_home(self, blog_title="", blog_body="", error=""):
        blog_posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")

        self.render("homepage.html", blog_title = blog_title,
                    blog_body = blog_body, error = error,
                    blog_posts = blog_posts)

    def get(self):
        self.render_home()

    def post(self):
        blog_title = self.request.get("blog_title")
        blog_body = self.request.get("blog_body")

        if blog_title and blog_body:
            new_blog = BlogPost(blog_title = blog_title, blog_body = blog_body)
            new_blog.put()

            self.redirect("/")
        else:
            no_input_error = "Pleast enter a title and a blog entry"
            self.render_home(blog_title, blog_body, no_input_error)

# Links to a single blog post from the front page
class ViewPostHandler(Handler):
    def get(self, id):
        id = int(id)
        single_post = BlogPost.get_by_id(id)

        if single_post:
            self.render("single_blog_post.html", single_post = single_post)
        else:
            self.write("<h3>This post does not exist</h3>")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    webapp2.Route('/<id:\d+>', ViewPostHandler)
], debug=True)
