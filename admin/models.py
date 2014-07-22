import uuid
from google.appengine.ext import ndb

class AccessToken(ndb.Model):
    token = ndb.StringProperty()

    @classmethod
    def is_authorized(cls, token):
        query = cls.query(AccessToken.token == token)
        access_token = query.get()
        return access_token != None

    @classmethod
    def get_all(cls):
        query = cls.query()
        return query.fetch()

    @classmethod
    def generate_new_token(cls):
        token = cls()
        token.token = uuid.uuid4().hex
        token.put()
        return token

    @classmethod
    def delete_token(cls, token_value):
        query = cls.query()
        query.filter(cls.token == token_value)
        token = query.get()
        if token:
            token.key.delete()
