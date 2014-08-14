android_crash_reports
=====================

Python / Google App Engine web service for handling ACRA crash reports
for Android devices

Usage
=====

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
