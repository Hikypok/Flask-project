from flask_wtf import FlaskForm
from flask import url_for, session, redirect, flash, render_template
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email
from ..db_session import create_session
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash


class RegisterForm(FlaskForm):
    nickname = StringField("Никнейм", validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    about = TextAreaField("О себе", validators=[Length(max=300)])
    password = PasswordField("Пароль", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Зарегистрироваться")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")


def auth(app):
    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            db_sess = create_session()
            user = User(
                nickname=form.nickname.data,
                email = form.email.data,
                hashed_password = generate_password_hash(form.password.data))
            db_sess.add(user)
            db_sess.commit()
            db_sess.close()
            flash("Регистрация успешна!", "success")
            return redirect(url_for("login"))
        return render_template("autorezation/register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            db_sess = create_session()
            user = db_sess.query(User).filter(User.email == form.email.data).first()
            if user and check_password_hash(user.hashed_password, form.password.data):
                session['user_id'] = user.id
                db_sess.close()
                return redirect(url_for('index'))
            flash('Неверный email или пароль', 'danger')
            db_sess.close()
        return render_template('autorezation/login.html', form=form)

    @app.route("/logout")
    def logout():
        session.pop("user_id", None)
        return redirect(url_for("index"))
