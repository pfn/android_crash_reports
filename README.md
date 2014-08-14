android_crash_reports
=====================

Python / Google App Engine web service for handling ACRA crash reports
for Android devices

Usage
=====

1. Deploy to appengine.

2. Set the `@ReportsCrashes` annotation on your `Application` context.
```
@ReportsCrashes(
        formKey = "",
        formUri = "http://APP_NAME.appspot.com/api/crashreport"
)
```

3. Edit `is_authorized()` in `crashreports/api.py` to allow your applications'
package names.

4. Go
