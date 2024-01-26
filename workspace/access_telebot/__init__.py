
from __future__ import absolute_import, unicode_literals
import sys

if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
    from .celery_config import app as celery_app
    __all__ = ('celery_app',)
