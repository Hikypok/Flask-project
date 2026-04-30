from flask import render_template
from ..db_session import create_session
from ..models import Review
from sqlalchemy.orm import joinedload


def init_main_routes(app):
    @app.route("/")
    def index():
        db_sess = create_session()
        reviews = db_sess.query(Review).options(joinedload(Review.author)).order_by(Review.created_date.desc()).all()
        db_sess.close()

        return render_template("index.html", reviews=reviews)