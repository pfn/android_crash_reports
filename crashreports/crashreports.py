import os
import webapp2
from google.appengine.ext import webapp, ndb
from google.appengine.ext.webapp import template
from models import CrashReport, CrashReportGroup
from utils.decorators import cached
from time import mktime, time

webapp.template.register_template_library('crashreports.templatefilters')

def add_ts(report):
    report.ts = int(mktime(report.created_at.timetuple()))
    return report

class CrashReportListHandler(webapp2.RequestHandler):

    def get(self):
        # Build a dictionary of crash reports as {report.package_name: report}
        query = CrashReportGroup.query()
        pairs = query.map(lambda x: (x.package_name, x.report_count()))
        reports = {k: v for (k, v) in pairs}

        template_values = {
            'reports': reports,
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/package_list.html')
        return self.response.write(template.render(path, template_values))

class CrashReportsForPackageHandler(webapp2.RequestHandler):
    def get(self, package_name):
        reports = CrashReport.for_package(package_name)
        reports = map(add_ts, reports)
        reports.sort(lambda x,y: y.ts - x.ts)

        template_values = {
            'pkg': package_name,
            'reports': reports,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        return self.response.write(template.render(path, template_values))

class CrashReportDeleteHandler(webapp2.RequestHandler):
    def post(self, package_name, report_id):
        group = CrashReportGroup.get_group(package_name)
        report = CrashReport.get_by_id(long(report_id), parent=group.key)
        report.key.delete()
        self.redirect("/reports/package/%s?ts=%f" % (package_name, time()))

class CrashReportDeletesHandler(webapp2.RequestHandler):
    def post(self, package_name):
        group = CrashReportGroup.get_group(package_name)
        selected = self.request.get("selected", allow_multiple=True)
        selected = map(lambda s: ndb.Key(CrashReport, long(s), parent=group.key), selected)
        ndb.delete_multi(selected)
        self.redirect("/reports/package/%s?ts=%f" % (package_name, time()))

class CrashReportHandler(webapp2.RequestHandler):
    def get(self, package_name, report_id):
        group = CrashReportGroup.get_group(package_name)
        report = CrashReport.get_by_id(long(report_id), parent=group.key)
        report = add_ts(report)

        reports = CrashReport.for_package(package_name)
        reports = map(add_ts, reports)
        reports.sort(lambda x,y: y.ts - x.ts)
        index = map(lambda x: x.key.id(), reports).index(report.key.id())
        if index == 0:
            prev = None
        else:
            prev = reports[index - 1]
        l = len(reports)

        if index == l - 1:
            next = None
        else:
            next = reports[index + 1]

        template_values = {
            'next': next,
            'report': report,
            'prev': prev,
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/crashreport.html')
        self.response.out.write(template.render(path, template_values))

class CrashPackageRedirectHandler(webapp2.RequestHandler):
    def get(self, package):
        self.redirect('/reports/package/%s' % package)

class CrashReportsRedirectHandler(webapp2.RequestHandler):
    def get(self, ignored):
        self.redirect('/reports/')

app = webapp2.WSGIApplication([
    ('/reports/package/(.+)/delete/id/(\d+)', CrashReportDeleteHandler),
    ('/reports/package/(.+)/delete',          CrashReportDeletesHandler),
    ('/reports/package/(.+)/id/(\d+)',        CrashReportHandler),
    ('/reports/package/(.+)/id/?',            CrashPackageRedirectHandler),
    ('/reports/package/(.+?)/?',              CrashReportsForPackageHandler),
    ('/reports/(.+)',                         CrashReportsRedirectHandler),
    ('/reports/',                             CrashReportListHandler),
    ], debug=True)
