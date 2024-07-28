from flask import flash, url_for, redirect, render_template
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from configurations.config import app, db, login_manager
from configurations.forms import LoginForm, RegisterForm
from configurations.users import UserLogin
from configurations.settings import main_menu
from configurations.models import UsersDB, ProfileDB, ChannelInformationDB, PostsDB, CommentsDB

from profile import profile_blueprint
from posts import post_blueprint

app.register_blueprint(profile_blueprint, url_prefix='/profile')
app.register_blueprint(post_blueprint, url_prefix='/posts')


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().from_db(user_id, UsersDB)


@app.route('/datas')
def _datas():
    UsersDB.generate_fake(100)
    ProfileDB.generate_fake(100)
    ChannelInformationDB.generate_fake(100)
    PostsDB.generate_fake(200)
    CommentsDB.generate_fake(1000)
    PostsDB.set_comments()

    return 'complite'


@app.route('/')
def index():
    return render_template('index.html', menu=main_menu)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Вы уже вошли в акаунт, выйдите из профиля, чтобы войти снова.', 'light_error')
        return redirect(url_for('profile.profile'))

    form = LoginForm()

    if form.validate_on_submit():
        user = UsersDB.query.filter_by(email=form.email.data).first()

        if user and user.name == form.name.data and check_password_hash(user.password, form.password.data):
            total_user_login = UserLogin().create(user)
            login_user(total_user_login)
            flash('Вы успешно вошли в акаунт', 'success')
            return redirect(url_for('index'))
        else:
            flash('Что-то пошло не так, попробуйте снова', 'error')

    return render_template('login.html', title='авторизация', menu=main_menu, form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Вы уже зарегестрированны, выйдите из профиля, чтобы войти зарегестрироваться снова.', 'light_error')
        return redirect(url_for('logout'))

    form = RegisterForm()

    if form.validate_on_submit():
        password_hash = generate_password_hash(form.repeat_password.data)

        user_data = {
            'name': form.name.data,
            'email': form.email.data,
            'password': password_hash,
        }

        try:
            user = UsersDB(**user_data)
            db.session.add(user)
            db.session.commit()

            this_user = UsersDB.query.filter_by(email=form.email.data).first()

            try:
                profile_ = ProfileDB(profile_id=this_user.id)
                db.session.add(profile_)
                db.session.commit()
            except Exception as error:
                print(f'Произошла ошибка в register2 {error}')
                flash('Что-то пошло не так, попробуйте снова', 'error')

            try:
                channel = ChannelInformationDB(channel_information_id=this_user.id)
                db.session.add(channel)
                db.session.commit()
            except Exception as error:
                print(f'Произошла ошибка в register2 {error}')
                flash('Что-то пошло не так, попробуйте снова', 'error')

            flash('Регистрация прошла успешно', 'success')
            return redirect(url_for('login'))

        except Exception as error:
            print(f'Произошла ошибка в register {error}')
            flash('Что-то пошло не так, попробуйте снова', 'error')

    return render_template('register.html', title='регистрация', menu=main_menu, form=form)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run()
