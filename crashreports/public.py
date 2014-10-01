import webapp2
from models import CrashReport, CrashReportGroup, CrashReportTrace
from google.appengine.ext import webapp, ndb
import logging
import os
from time import mktime
from functools import partial
from google.appengine.ext.webapp import template

webapp.template.register_template_library('crashreports.templatefilters')

def add_ts(attr, report, ts = "ts"):
    t = getattr(report, attr)
    if not t:
        t = getattr(report, "created_at")
    setattr(report, ts, int(mktime(t.timetuple())))
    return report

class CrashReportHandler(webapp2.RequestHandler):
    def get(self, package_name, trace_id):
        group = CrashReportGroup.get_by_id(package_name)
        if not group:
            self.response.status = 404
            self.response.write("Not found")
            return

        trace = CrashReportTrace.get_by_id(trace_id, parent=group.key)
        if not trace:
            self.response.status = 404
            self.response.write("Not found")
            return

        trace = add_ts("created_at", trace, ts = "created_ts")

        reports = CrashReport.for_trace(package_name, trace_id)
        reports = map(partial(add_ts, "created_at"), reports)
        reports = map(partial(add_ts, "user_crash_date", ts = "crash_ts"), reports)
        reports.sort(lambda x,y: y.ts - x.ts)

        template_values = {
            'report':  trace,
            'reports': reports,
        }

        path = os.path.join(os.path.dirname(__file__), 'templates/publicreport.html')
        self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([
    ('/public/(.+)/(\w+)',        CrashReportHandler),
    ], debug=True)
