from flask import Flask
from app import db_session
from .pages.autorezation import auth
from .pages.profile import init_profile_routes
from .pages.main import init_main_routes
from .pages.posts import init_posts_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = 'alina_228_lol_kek_bebebe'


def main():
    db_session.global_init("blogs.db")
    auth(app)
    init_profile_routes(app)
    init_main_routes(app)
    init_posts_routes(app)
    app.run(port=8080, host="127.0.0.1", debug=True)


if __name__ == "__main__":
    main()