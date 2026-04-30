from flask import render_template, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length
from ..db_session import create_session
from ..models import User
from sqlalchemy.orm import joinedload


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
                    flash("Этот никнейм уже занят другим пользователем", "danger")
                else:
                    user.nickname = form.nickname.data
                    user.about = form.about.data
                    db_sess.commit()
                    flash("Профиль успешно обновлён!", "success")
                    return redirect(url_for('profile'))

            return render_template('edit_profile.html', form=form, user=user)
        finally:
            db_sess.close()
class EditProfileForm(FlaskForm):
    nickname = StringField("Никнейм", validators=[DataRequired(), Length(min=2, max=30)])
    about = TextAreaField("О себе", validators=[Length(max=300)])
    submit = SubmitField("Сохранить изменения")
