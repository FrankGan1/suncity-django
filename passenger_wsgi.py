"""
Entry point used by CyberPanel's "Python App" feature (OpenLiteSpeed +
Passenger). CyberPanel looks for a `passenger_wsgi.py` file at the
application root exposing a WSGI callable named `application`.

This is NOT used for local development or for a Gunicorn/systemd
deployment — those use suncity_django/wsgi.py directly. See README.md.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'suncity_django.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
