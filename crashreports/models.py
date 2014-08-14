from google.appengine.ext import ndb
import hashlib

class CrashReportGroup(ndb.Model):
    created_at              = ndb.DateTimeProperty(auto_now_add=True)
    latest_crash_date       = ndb.DateTimeProperty()
    package_name            = ndb.StringProperty()

    @classmethod
    def get_group(cls, package_name):
        return cls.get_or_insert(package_name)

    def report_count(self):
        return CrashReportTrace.query(ancestor=self.key).count()

    def _pre_put_hook(self):
        self.package_name = self.key.string_id()

class CrashReportTrace(ndb.Model):
    created_at        = ndb.DateTimeProperty(auto_now_add=True)
    latest_crash_date = ndb.DateTimeProperty()
    package_name      = ndb.StringProperty()
    stack_hash        = ndb.StringProperty()
    stack_trace       = ndb.TextProperty()
    stack_summary     = ndb.StringProperty()

    @classmethod
    def for_package(cls, package_name):
        return cls.query(cls.package_name == package_name).order(
            -cls.latest_crash_date).fetch()

    @classmethod
    def get_trace(cls, groupkey, trace):
        sha1 = hashlib.sha1()

        stack = '\n'.join(trace.split('\n')[1:])
        sha1.update(stack)
        digest = sha1.hexdigest()

        return cls.get_or_insert(digest, parent=groupkey, **{
          'package_name':  groupkey.string_id(),
          'stack_trace':   stack,
          'stack_summary': CrashReportTrace.get_stack_summary(
              trace, groupkey.string_id()),
        })

    def _pre_put_hook(self):
        self.stack_hash = self.key.string_id()

    def report_count(self):
        return CrashReport.query(ancestor=self.key).count()

    @classmethod
    def get_stack_summary(cls, stack_trace, package_name):
        lines = stack_trace.split('\n')
        summary = lines[0]

        for line in lines[1:]:
            if line.find(package_name) > 0:
                summary = summary + ' ' + line.strip('\t')
                break

        # Stack trace summary = first line + topmost occurance of package_name
        return summary[:500]


class CrashReport(ndb.Model):
    created_at              = ndb.DateTimeProperty(auto_now_add=True)
    android_version         = ndb.StringProperty()
    app_version_code        = ndb.StringProperty()
    app_version_name        = ndb.StringProperty()
    available_mem_size      = ndb.StringProperty()
    logcat                  = ndb.TextProperty()
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
    stack_hash              = ndb.StringProperty()
    stack_trace             = ndb.TextProperty()
    stack_summary           = ndb.StringProperty()
    total_mem_size          = ndb.TextProperty()
    user_app_start_date     = ndb.DateTimeProperty()
    user_crash_date         = ndb.DateTimeProperty()

    @classmethod
    def for_trace(cls, package_name, trace):
        return cls.query(cls.package_name == package_name and
            cls.stack_hash == trace).order(-cls.created_at).fetch(limit=50)
