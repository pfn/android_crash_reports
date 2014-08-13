import os
import webapp2
from google.appengine.ext import webapp, ndb
from google.appengine.ext.webapp import template
from models import CrashReport, CrashReportGroup, CrashReportTrace
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
        reports = CrashReportTrace.for_package(package_name)
        reports = map(add_ts, reports)
        reports.sort(lambda x,y: y.ts - x.ts)

        template_values = {
            'pkg': package_name,
            'reports': reports,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/list.html')
        return self.response.write(template.render(path, template_values))

class CrashReportDeleteHandler(webapp2.RequestHandler):
    def post(self, package_name, trace_id):
        group = CrashReportGroup.get_group(package_name)
        trace = CrashReportTrace.get_trace(group.key, trace_id)
        ndb.delete_multi(ndb.Query(ancestor=trace.key).iter(keys_only=True))
        trace.key.delete()
        self.redirect("/reports/package/%s?ts=%f" % (package_name, time()))

class CrashReportDeletesHandler(webapp2.RequestHandler):
    def post(self, package_name):
        group = CrashReportGroup.get_group(package_name)
        selected = self.request.get_all("selected")
        selected = map(lambda s: ndb.Key(
            CrashReportTrace, s, parent=group.key), selected)
        for trace in selected:
            ndb.delete_multi(ndb.Query(ancestor=trace).iter(keys_only=True))
        ndb.delete_multi(selected)
        self.redirect("/reports/package/%s?ts=%f" % (package_name, time()))

class CrashReportHandler(webapp2.RequestHandler):
    def get(self, package_name, trace_id):
        group = CrashReportGroup.get_group(package_name)
        trace = CrashReportTrace.get_by_id(trace_id, parent=group.key)
        trace = add_ts(trace)

        traces = CrashReportTrace.for_package(package_name)
        traces = map(add_ts, traces)
        traces.sort(lambda x,y: y.ts - x.ts)
        index = map(lambda x: x.key.string_id(), traces).index(trace.key.string_id())
        reports = CrashReport.for_trace(package_name, trace_id)
        reports = map(add_ts, reports)
        reports.sort(lambda x,y: y.ts - x.ts)

        if index == 0:
            prev = None
        else:
            prev = traces[index - 1]
        l = len(traces)

        if index == l - 1:
            next = None
        else:
            next = traces[index + 1]

        template_values = {
            'next':    next,
            'report':  trace,
            'prev':    prev,
            'reports': reports,
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
    ('/reports/package/(.+)/delete/id/(\w+)', CrashReportDeleteHandler),
    ('/reports/package/(.+)/delete',          CrashReportDeletesHandler),
    ('/reports/package/(.+)/id/(\w+)',        CrashReportHandler),
    ('/reports/package/(.+)/id/?',            CrashPackageRedirectHandler),
    ('/reports/package/(.+?)/?',              CrashReportsForPackageHandler),
    ('/reports/(.+)',                         CrashReportsRedirectHandler),
    ('/reports/',                             CrashReportListHandler),
    ], debug=True)
