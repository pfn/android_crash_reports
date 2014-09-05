android_crash_reports
=====================

Python / Google App Engine web service for handling ACRA crash reports
for Android devices. Polymerized.

Screenshots
===========

* http://ezscreens.appspot.com/view/f22c/hanhuy-acra+all+packages
* http://ezscreens.appspot.com/view/4aac/hanhuy-acra+crash+list
* http://ezscreens.appspot.com/view/ea41/hanhuy-acra+crash+report

Usage
=====

* Install `node.js` and `npm install vulcanize`
* `vulcanize -s --inline -o js/polymer.html js/dependencies.html`
* Edit `app.yaml` set `application` to `APP_NAME`
* Edit `is_authorized()` in `crashreports/api.py` to allow your applications'
  package names.
* Deploy to appengine.
* Set the `@ReportsCrashes` annotation on your `Application` context.
```
@ReportsCrashes(
        formKey = "",
        formUri = "http://APP_NAME.appspot.com/api/crashreport"
)
```
* Go
