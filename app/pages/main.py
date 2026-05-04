from flask import render_template, request
from ..db_session import create_session
from ..models import Review
from sqlalchemy.orm import joinedload
from sqlalchemy import desc, asc, func


def init_main_routes(app):
    @app.route("/")
    def index():
        db_sess = create_session()

        category = request.args.get('category', '')
        search = request.args.get('search', '').strip()
        sort = request.args.get('sort', 'newest')

        query = db_sess.query(Review).options(joinedload(Review.author))

        if category and category in ['books', 'movies', 'places']:
            query = query.filter(Review.category == category)

        if search:
            search_clean = ' '.join(search.lower().split())
            search_pattern = f"%{search_clean}%"
            query = query.filter(
                func.lower(Review.title).like(search_pattern) |
                func.lower(Review.content).like(search_pattern))

        if sort == 'oldest':
            query = query.order_by(Review.created_date.asc())
        elif sort == 'rating_high':
            query = query.order_by(Review.rating.desc(), Review.created_date.desc())
        elif sort == 'rating_low':
            query = query.order_by(Review.rating.asc())
        else:
            query = query.order_by(Review.created_date.desc())

        reviews = query.all()
        db_sess.close()

        return render_template(
            "index.html",
            reviews=reviews,
            current_category=category,
            current_search=search,
            current_sort=sort)