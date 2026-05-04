import sys
import os

path = '/home/hikypok/myproject'
if path not in sys.path:
    sys.path.append(path)

os.environ['PYTHONPATH'] = path

from app import app as application