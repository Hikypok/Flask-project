from flask import Flask
from . import db_session
from .pages.autorezation import auth
from .pages.profile import init_profile_routes
from .pages.main import init_main_routes
from .pages.posts import init_posts_routes
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'alina_228_lol_kek_bebebe'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'avatars')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['REVIEW_PHOTO_FOLDER'] = os.path.join(basedir, 'static', 'review_photos')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['REVIEW_PHOTO_FOLDER'], exist_ok=True)

db_session.global_init("blogs.db")
auth(app)
init_profile_routes(app)
init_main_routes(app)
init_posts_routes(app)


def main():
    app.run(port=8080, host="127.0.0.1", debug=True)


if __name__ == "__main__":
    main()