from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, FileField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length, Email, NumberRange, Optional
from flask_wtf.file import FileAllowed, FileRequired


class LoginForm(FlaskForm):
    name = StringField('Псевдоним', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(min=6, max=50)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=50)])
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    name = StringField('Псевдоним', validators=[DataRequired(), Length(min=3, max=20)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(min=6, max=50)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=50)])
    repeat_password = PasswordField('Пароль', validators=[EqualTo('password')])
    submit = SubmitField('Зарегестрироваться')


class ProfileForm(FlaskForm):
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6, max=50)])
    avatar = FileField('Аватар', validators=[FileRequired(), FileAllowed(['png', 'jpg'])])
    submit = SubmitField('Отправить')


class UserInfoForm(FlaskForm):
    nick = StringField('Псевдоним', validators=[Optional(), Length(min=3, max=20)])
    name = StringField('Имя', validators=[Optional(), Length(min=3, max=20)])
    sure_name = StringField('Фамилия', validators=[Optional(), Length(min=3, max=20)])
    age = IntegerField('Возраст', validators=[Optional(), NumberRange(min=12, max=100)])
    gender = StringField('Гендер', validators=[Optional(), Length(min=1, max=20)])
    city = StringField('Город', validators=[Optional(), Length(min=3, max=20)])
    about_yourself = TextAreaField('О себе', validators=[Optional(), Length(min=3, max=400)])
    submit = SubmitField('Обновить')


class ChannelInfoForm(FlaskForm):
    about_channel = TextAreaField('О канале', validators=[Optional(), Length(min=3, max=400)])
    submit = SubmitField('Обновить')


class AddPostForm(FlaskForm):
    title = StringField('Название статьи', validators=[DataRequired(), Length(min=3, max=50)])
    main = TextAreaField('Основная часть статьи', validators=[DataRequired(), Length(min=3, max=2000)])
    submit = SubmitField('Создать')


class SetCommentForm(FlaskForm):
    comment = TextAreaField('Комментарий', validators=[DataRequired(), Length(min=3, max=2000)])
    submit = SubmitField('Опубликовать')
