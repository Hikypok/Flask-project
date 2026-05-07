from flask import render_template, redirect, url_for, flash, session, current_app, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, SubmitField, FileField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange
from werkzeug.utils import secure_filename
from PIL import Image
import os
import time
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
    address = StringField("Адрес места")
    photo_file = FileField("Фото к отзыву")
    submit = SubmitField("Опубликовать")
    lat = HiddenField('lat')
    lon = HiddenField('lon')


def save_review_photo(file):
    if not file or file.filename == '':
        return None
    filename = secure_filename(file.filename)

    if '.' not in filename:
        print(f"Файл без расширения: {filename}")
        return None
    ext = filename.rsplit('.', 1)[1].lower()
    allowed_ext = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if ext not in allowed_ext:
        print(f"Недопустимый формат: {ext}")
        return None
    new_filename = f"review_{int(time.time())}.{ext}"
    filepath = os.path.join(current_app.config['REVIEW_PHOTO_FOLDER'], new_filename)
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        img = Image.open(file)
        img.save(filepath, format=ext.upper() if ext != 'jpg' else 'JPEG', quality=90)
        return new_filename
    except Exception as e:
        print(f"Ошибка обработки фото: {e}")
        return None


def init_posts_routes(app):
    @app.route("/review/create", methods=["GET", "POST"])
    def create_review():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        form = ReviewForm()
        if form.validate_on_submit():
            db_sess = create_session()
            try:
                photo_name = None
                if form.photo_file.data:
                    photo_name = save_review_photo(form.photo_file.data)
                new_review = Review(
                    title=form.title.data,
                    content=form.content.data,
                    rating=form.rating.data,
                    category=form.category.data,
                    author_id=session['user_id'],
                    address=form.address.data.strip() if form.category.data == 'places' and form.address.data else None,
                    photo=photo_name
                )
                db_sess.add(new_review)
                db_sess.commit()
                flash("✅ Отзыв опубликован!", "success")
                return redirect(url_for('index'))
            except Exception as e:
                db_sess.rollback()
                flash(f"Ошибка: {e}", "danger")
            finally:
                db_sess.close()

        return render_template("create.html", form=form)

    @app.route("/review/<int:review_id>/delete", methods=["POST"])
    def delete_review(review_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        db_sess = create_session()
        try:
            review = db_sess.query(Review).get(review_id)

            if not review or review.author_id != session['user_id']:
                flash("Нельзя удалить чужой отзыв!", "danger")
                return redirect(url_for('index'))

            if review.photo:
                photo_path = os.path.join(current_app.config['REVIEW_PHOTO_FOLDER'], review.photo)
                if os.path.exists(photo_path):
                    os.remove(photo_path)

            db_sess.delete(review)
            db_sess.commit()
            flash("Отзыв удалён", "success")
            return redirect(request.referrer or url_for('profile'))
        finally:
            db_sess.close()