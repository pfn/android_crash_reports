import os
import webapp2

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.redirect('/reports/')

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ], debug=True)
