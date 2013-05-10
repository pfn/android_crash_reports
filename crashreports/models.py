from google.appengine.ext import ndb

class CrashReport(ndb.Model):
    created_at              = ndb.DateTimeProperty(auto_now_add=True)
    android_version         = ndb.StringProperty()
    app_version_code        = ndb.StringProperty()
    app_version_name        = ndb.StringProperty()
    available_mem_size      = ndb.StringProperty()
    brand                   = ndb.TextProperty()
    build                   = ndb.TextProperty()
    crash_configuration     = ndb.TextProperty()
    device_features         = ndb.TextProperty()
    display                 = ndb.TextProperty()
    environment             = ndb.TextProperty()
    file_path               = ndb.TextProperty()
    initial_configuration   = ndb.TextProperty()
    installation_id         = ndb.TextProperty()
    package_name            = ndb.StringProperty()
    model                   = ndb.StringProperty()
    product                 = ndb.TextProperty()
    report_id               = ndb.TextProperty()
    settings_secure         = ndb.TextProperty()
    settings_system         = ndb.TextProperty()
    shared_preferences      = ndb.TextProperty()
    stack_trace             = ndb.TextProperty()
    stack_summary           = ndb.StringProperty()
    total_mem_size          = ndb.TextProperty()
    user_app_start_date     = ndb.DateTimeProperty()
    user_crash_date         = ndb.DateTimeProperty()

    @classmethod
    def get_all(cls):
        query = cls.query()
        return query.fetch()

    @classmethod
    def for_package(cls, package_name):
        query = cls.query(cls.package_name == package_name)
        return query.fetch()
