import sys
import os

path = '/home/Hikypok/Приятный досуг'
if path not in sys.path:
    sys.path.append(path)

os.environ['PYTHONPATH'] = path

from app import app as application