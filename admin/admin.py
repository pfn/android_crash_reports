import os
import webapp2
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template
from models import AccessToken

class AccessTokenHandler(webapp2.RequestHandler):
    def get(self):
        tokens = AccessToken.get_all()
        self.render_template(tokens)

    def post(self):
        AccessToken.generate_new_token()
        tokens = AccessToken.get_all()
        self.render_template(tokens)

    def delete(self):
        token = AccessToken.delete_token(self.request.get('token'))
        tokens = AccessToken.get_all()
        self.render_template(tokens)
        
    def render_template(self, tokens):
        template_values = {
            'tokens': tokens,
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/tokens.html')
        self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([
    ('/admin/tokens', AccessTokenHandler),
    ], debug=True)
