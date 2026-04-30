from flask import render_template, redirect, url_for, flash, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange
from ..db_session import create_session
from ..models import Review


class ReviewForm(FlaskForm):
    title = StringField("Заголовок", validators=[DataRequired(), Length(max=100)])
    content = TextAreaField("Текст отзыва", validators=[DataRequired()])
    rating = IntegerField("Рейтинг (1-10)", validators=[DataRequired(), NumberRange(min=1, max=10)])
    category = SelectField("Категория", choices=[
        ('books', 'Книга'),
        ('movies', 'Фильм'),
        ('places', 'Место')], validators=[DataRequired()])

    lat = HiddenField('lat')
    lon = HiddenField('lon')
    address = StringField("Адрес места")
    submit = SubmitField("Опубликовать")

def init_posts_routes(app):
    @app.route("/review/create", methods=["GET", "POST"])
    def create_review():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        form = ReviewForm()

        if form.validate_on_submit():
            print(f"DEBUG: category={form.category.data}, address='{form.address.data}'")

            db_sess = create_session()
            try:
                new_review = Review(
                    title=form.title.data,
                    content=form.content.data,
                    rating=form.rating.data,
                    category=form.category.data,
                    author_id=session['user_id'],
                    address=form.address.data.strip() if form.category.data == 'places' and form.address.data else None,
                    lat=float(form.lat.data) if form.lat.data else None,
                    lon=float(form.lon.data) if form.lon.data else None
                )
                db_sess.add(new_review)
                db_sess.commit()
                print(f"Saved: address='{new_review.address}'")
                flash("Отзыв опубликован!", "success")
                return redirect(url_for('index'))
            except Exception as e:
                db_sess.rollback()
                print(f"Error: {e}")
                flash(f"Ошибка: {e}", "danger")
            finally:
                db_sess.close()

        return render_template("create.html", form=form)