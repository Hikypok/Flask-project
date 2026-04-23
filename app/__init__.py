from flask import Flask
from app import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'alina_228_lol_kek_bebebe'


def main():
    db_session.global_init("blogs.db")
    app.run(port=8080, host="127.0.0.1")


if __name__ == "__main__":
    main()
