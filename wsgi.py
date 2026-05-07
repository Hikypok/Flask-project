import sys
import os

path = '/home/hikypok/myproject'
if path not in sys.path:
    sys.path.append(path)

from app import app

from app import db_session
db_session.global_init("blogs.db")

from app.pages.autorezation import auth
from app.pages.profile import init_profile_routes
from app.pages.main import init_main_routes
from app.pages.posts import init_posts_routes

auth(app)
init_profile_routes(app)
init_main_routes(app)
init_posts_routes(app)

application = app