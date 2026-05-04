from flask import render_template, session, redirect, url_for, flash, current_app, request
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, FileField
from wtforms.validators import DataRequired, Length
from ..db_session import create_session
from ..models import User
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename  # этот модуль защищает от злоумышленников, приводя название файла в нормальный вид
from PIL import Image
import os


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_avatar(file, user_id):
    if not file or file.filename == '':
        return None

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()

    allowed_ext = current_app.config['ALLOWED_EXTENSIONS']
    if ext not in allowed_ext:
        return None

    new_filename = f"user_{user_id}_avatar.{ext}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename)

    try:
        img = Image.open(file)
        width, height = img.size
        new_size = min(width, height)
        left = (width - new_size) / 2
        top = (height - new_size) / 2
        right = (width + new_size) / 2
        bottom = (height + new_size) / 2
        img = img.crop((left, top, right, bottom))
        img = img.resize((300, 300), Image.Resampling.LANCZOS)

        img.save(filepath, quality=90)
        return new_filename
    except Exception as e:
        return None


def init_profile_routes(app):
    @app.route("/profile")
    def profile():
        if 'user_id' not in session:
            flash('Для просмотра профиля нужно войти', 'warning')
            return redirect(url_for('login'))
        db_sess = create_session()
        try:
            user = db_sess.query(User).options(joinedload(User.reviews)).get(session['user_id'])
            if not user:
                session.pop('user_id', None)
                return redirect(url_for('login'))
            return render_template('profile.html', user=user)
        finally:
            db_sess.close()

    @app.route("/profile/edit", methods=["GET", "POST"])
    def edit_profile():
        if 'user_id' not in session:
            return redirect(url_for('login'))
        db_sess = create_session()
        try:
            user = db_sess.query(User).get(session['user_id'])
            if not user:
                session.pop('user_id', None)
                return redirect(url_for('login'))

            form = EditProfileForm(obj=user)

            if form.validate_on_submit():
                taken = db_sess.query(User).filter(
                    User.nickname == form.nickname.data,
                    User.id != user.id
                ).first()

                if taken:
                    flash("Этот никнейм уже занят", "danger")
                else:
                    user.nickname = form.nickname.data
                    user.about = form.about.data

                    if form.avatar_file:
                        old_avatar = user.avatar
                        new_avatar = save_avatar(form.avatar_file.data, user.id)
                        if new_avatar:
                            if old_avatar and old_avatar != new_avatar:
                                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_avatar)
                                if os.path.exists(old_path):
                                    os.remove(old_path)
                            user.avatar = new_avatar
                        else:
                            flash("Не удалось сохранить аватарку. Проверьте формат файла.", "danger")
                    db_sess.commit()
                    flash(" Профиль успешно обновлён!", "success")
                    return redirect(url_for('profile'))

            return render_template('edit_profile.html', form=form, user=user)
        finally:
            db_sess.close()

class EditProfileForm(FlaskForm):
    nickname = StringField("Никнейм", validators=[DataRequired(), Length(min=2, max=30)])
    about = TextAreaField("О себе", validators=[Length(max=300)])
    avatar = StringField("Аватарка", render_kw={"readonly": True})
    avatar_file = FileField("Загрузить аватарку", validators=[])
    submit = SubmitField("Сохранить изменения")
