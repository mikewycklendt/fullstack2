import logging
import sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/html/demo1/')
from application import app as application
application.secret_key = 'super_secret_key'