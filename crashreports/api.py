import os
import urlparse
import webapp2
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from dateutil import parser as dateparser
from models import CrashReport, CrashReportGroup, CrashReportTrace
from admin.models import AccessToken

class NewCrashReportHandler(webapp2.RequestHandler):
    def post(self):
        if self.is_authorized(self.request):
            # Parse and save the crash report
            report = self.parse_crash_report(self.request)
            report.put()

            # Grab the app's base url
            url_info = urlparse.urlparse(self.request.url)
            base_url = url_info.scheme + '://' + url_info.netloc

            # Return a response
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.write('Report %d saved' % report.key.id())
        else:
            # No valid access token
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.set_status(401)
            self.response.write('Invalid access token')

    def is_authorized(self, request):
        # Check if there's a valid access token in the request
        return request.get('PACKAGE_NAME').startswith("com.hanhuy")

    def parse_crash_report(self, request):
        # Get or create the parent report group for this crash report
        package_name = request.get('PACKAGE_NAME')
        stack_trace  = request.get('STACK_TRACE')
        report_group = CrashReportGroup.get_group(package_name)
        report_trace = CrashReportTrace.get_trace(report_group.key, stack_trace)

        # Create a new crash report
        report = CrashReport(parent=report_trace.key)

        # stack trace
        report.stack_hash = report_trace.stack_hash
        report.stack_trace = stack_trace
        report.stack_summary = CrashReportTrace.get_stack_summary(
            stack_trace, package_name)

        # Parse POST body
        report.package_name             = package_name
        report.logcat                   = request.get('LOGCAT')
        report.android_version          = request.get('ANDROID_VERSION')
        report.app_version_code         = request.get('APP_VERSION_CODE')
        report.app_version_name         = request.get('APP_VERSION_NAME')
        report.available_mem_size       = request.get('AVAILABLE_MEM_SIZE')
        report.brand                    = request.get('BRAND')
        report.build                    = request.get('BUILD')
        report.crash_configuration      = request.get('CRASH_CONFIGURATION')
        report.device_features          = request.get('DEVICE_FEATURES')
        report.display                  = request.get('DISPLAY')
        report.environment              = request.get('ENVIRONMENT')
        report.file_path                = request.get('FILE_PATH')
        report.initial_configuration    = request.get('INITIAL_CONFIGURATION')
        report.installation_id          = request.get('INSTALLATION_ID')
        report.model                    = request.get('PHONE_MODEL')
        report.product                  = request.get('PRODUCT')
        report.report_id                = request.get('REPORT_ID')
        report.settings_secure          = request.get('SETTINGS_SECURE')
        report.settings_system          = request.get('SETTINGS_SYSTEM')
        report.shared_preferences       = request.get('SHARED_PREFERENCES')
        report.total_mem_size           = request.get('TOTAL_MEM_SIZE')

        # Coerce date strings into parseable format
        start_date = dateparser.parse(
            request.get('USER_APP_START_DATE'), ignoretz=True)
        crash_date = dateparser.parse(
            request.get('USER_CRASH_DATE'), ignoretz=True)
        report.user_app_start_date      = start_date
        report.user_crash_date          = crash_date

        # If this crash report's timestamp is more recent than its parent's
        # latest crash date, update the parent group
        if report_group.latest_crash_date == None or report.user_crash_date > report_group.latest_crash_date:
            report_group.latest_crash_date = report.user_crash_date
            report_group.put()


        return report

app = webapp2.WSGIApplication([
    ('/api/crashreport',        NewCrashReportHandler),
    ], debug=True)
