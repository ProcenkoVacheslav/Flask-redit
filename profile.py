from flask import Blueprint

from flask import flash, url_for, redirect, make_response, request, render_template, current_app
from flask_login import login_required, current_user, logout_user

from configurations.users import UpdateUserAvatar
from configurations.models import UsersDB, ProfileDB, ChannelInformationDB, PostsDB, LikesDB, FollowersDB
from configurations.settings import main_menu
from configurations.forms import UserInfoForm, ChannelInfoForm
from configurations.config import db

profile_blueprint = Blueprint('profile', __name__, template_folder='configurations/templates',
                              static_folder='configurations/static')


def get_datas(user_id, title):
    user = UsersDB.query.filter_by(id=user_id).first()

    user_profile = None
    user_chanel = None
    avatar = None

    try:
        user_profile = ProfileDB.query.filter_by(id=user_id).first()
        user_chanel = ChannelInformationDB.query.filter_by(id=user_id).first()
    except Exception as error:
        print(f'{error}')

    user_data = [
        {'title': 'Псевдоним', 'data': user.name},
        {'title': 'Имя', 'data': user_profile.name},
        {'title': 'Фамилия', 'data': user_profile.sure_name},
        {'title': 'Возраст', 'data': user_profile.age},
        {'title': 'Гендер', 'data': user_profile.gender},
        {'title': 'Город', 'data': user_profile.city},
        {'title': 'О себе', 'data': user_profile.about_yourself},
    ]

    folowers = user_chanel.followers
    my_folowers = user_chanel.you_follow
    chanel_info = user_chanel.channel_information
    posts_count = PostsDB.query.filter_by(author=user_id).count()
    likes_count = LikesDB.query.filter_by(user_id=user_id).count()

    if user_profile:
        avatar = user_profile.avatar

    all_datas = {
        'title': title,
        'menu': main_menu,
        'avatar': avatar,
        'user_data': user_data,
        'folowers': folowers,
        'my_folowers': my_folowers,
        'chanel_info': chanel_info,
        'date': user.date,
        'posts_count': posts_count,
        'likes_count': likes_count,
    }

    return all_datas


@profile_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def profile():
    all_datas = get_datas(current_user.get_id(), 'профиль')

    return render_template('profile.html', **all_datas)


@profile_blueprint.route('/get_profile/<user_id>')
@login_required
def get_profile(user_id):
    user = UsersDB.query.filter_by(id=user_id).first()

    all_datas = get_datas(user_id, f'профиль {user.name}')

    return render_template('user_profile.html', **all_datas, user_id=user_id)


@profile_blueprint.route('/change_information', methods=['GET', 'POST'])
@login_required
def change_information():
    form = UserInfoForm()

    user = UsersDB.query.filter_by(id=current_user.get_id()).first()
    profile_ = ProfileDB.query.filter_by(id=current_user.get_id()).first()

    current_datas = {
        'nick': user.name,
        'name': profile_.name,
        'sure_name': profile_.sure_name,
        'age': profile_.age,
        'gender': profile_.gender,
        'city': profile_.city,
        'about_yourself': profile_.about_yourself,
    }

    if form.validate_on_submit():

        profile_datas = {
            'name': form.name.data,
            'sure_name': form.sure_name.data,
            'age': form.age.data,
            'gender': form.gender.data,
            'city': form.city.data,
            'about_yourself': form.about_yourself.data,
        }

        nick = form.nick.data

        try:
            new_user = UsersDB.query.filter_by(id=current_user.get_id()).update({'name': nick})
            db.session.commit()

            try:
                new_profile = ProfileDB.query.filter_by(id=user.id).update(profile_datas)
                db.session.commit()

                assert new_profile is not None, 'new_profile is None'

            except Exception as error:
                flash('Произошла ошибка, попробуйте снова', 'error')
                print(f'Произошла ошибка в change_information {error}')

            assert new_user is not None, 'new_user is None'

            flash('Обновление информации прошло успешно', 'success')
            return redirect(url_for('profile.profile'))
        except Exception as error:
            flash('Произошла ошибка, попробуйте снова', 'error')
            print(f'Произошла ошибка в change_information {error}')
    else:
        form.about_yourself.data = profile_.about_yourself

    return render_template('change_information.html', menu=main_menu, title='новая информация о вас', form=form,
                           current_datas=current_datas)


@profile_blueprint.route('/change_chanel_information', methods=['GET', 'POST'])
@login_required
def change_chanel_information():
    form = ChannelInfoForm()

    channel = ChannelInformationDB.query.filter_by(id=current_user.get_id()).first()

    if form.validate_on_submit():
        try:
            new_channel = ChannelInformationDB.query.filter_by(id=current_user.get_id()).update(
                {'channel_information': form.about_channel.data})

            assert new_channel is not None, 'Что-то не так в change_chanel_information'

            db.session.commit()
            flash('Информация успешно обновлена', 'success')
            return redirect(url_for('profile.profile'))
        except Exception as error:
            flash('Произошла ошибка, попробуйте снова', 'error')
            print(f'Произошла ошибка в change_chanel_information {error}')
    else:
        if channel.channel_information:
            form.about_channel.data = channel.channel_information

    return render_template('change_chanel_information.html', menu=main_menu, title='новая информация о канале',
                           form=form)


def get_pagination_posts(author):
    page = request.args.get('page', 1, type=int)

    pagination = db.session.query(PostsDB, UsersDB, ProfileDB).select_from(PostsDB).filter_by(
        author=author).join(UsersDB).join(ProfileDB).order_by(PostsDB.date.desc()). \
        paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    this_posts = pagination.items

    return this_posts, pagination


@profile_blueprint.route('/my_posts')
@login_required
def my_posts():
    author = current_user.get_id()

    this_posts, pagination = get_pagination_posts(author)

    return render_template('my_posts.html', title='мои записи', menu=main_menu, posts=this_posts, pagination=pagination)


@profile_blueprint.route('/user_posts/<user_id>')
@login_required
def user_posts(user_id):
    user = UsersDB.query.filter_by(id=user_id).first()

    this_posts, pagination = get_pagination_posts(user_id)

    return render_template('my_posts.html', title=f'записи {user.name}', menu=main_menu, posts=this_posts,
                           pagination=pagination, user_id=user_id)


def get_pagination_like_posts(likes_id):
    page = request.args.get('page', 1, type=int)

    pagination = db.session.query(PostsDB, UsersDB, ProfileDB).select_from(PostsDB).filter(
        PostsDB.id.in_(likes_id)).join(UsersDB).join(ProfileDB).order_by(PostsDB.date.desc()). \
        paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    this_posts = pagination.items

    return this_posts, pagination


@profile_blueprint.route('/like_posts')
@login_required
def like_posts():
    likes_id = current_user.get_likes_id()
    followers_id = current_user.get_followers_id()

    this_posts, pagination = get_pagination_like_posts(likes_id)

    return render_template('like_posts.html', title='понравевшееся', menu=main_menu, posts=this_posts,
                           pagination=pagination, followers=followers_id, me=int(current_user.get_id()))


@profile_blueprint.route('/user_like_posts/<user_id>')
@login_required
def user_like_posts(user_id):
    user = UsersDB.query.filter_by(id=user_id).first()

    likes = LikesDB.query.filter_by(user_id=user_id).all()
    likes_id = [like.post_id for like in likes]
    followers_id = current_user.get_followers_id()

    this_posts, pagination = get_pagination_like_posts(likes_id)

    return render_template('like_posts.html', title=f'понравевшееся {user.name}', menu=main_menu, posts=this_posts,
                           pagination=pagination, followers=followers_id, me=int(current_user.get_id()))


def get_followers(user):
    persons = db.session.query(FollowersDB, UsersDB, ProfileDB).select_from(FollowersDB).filter_by(
        follower=user).join(UsersDB).join(ProfileDB).order_by(FollowersDB.date.desc())

    return persons


@profile_blueprint.route('/follow_you')
@login_required
def follow_you():
    followers_id = current_user.get_followers_id()

    persons = get_followers(current_user.get_id())

    return render_template('follow_you.html', title='подписаны на вас', menu=main_menu, persons=persons,
                           followers=followers_id, me=int(current_user.get_id()))


@profile_blueprint.route('/follow_user/<user_id>')
@login_required
def follow_user(user_id):
    user = UsersDB.query.filter_by(id=user_id).first()

    followers = FollowersDB.query.filter_by(user=user_id).all()
    followers_id = [follower.follower for follower in followers]

    persons = get_followers(user_id)

    return render_template('follow_you.html', title=f'подписаны на {user.name}', menu=main_menu, persons=persons,
                           followers=followers_id, me=int(current_user.get_id()), user=user.name)


@profile_blueprint.route('/you_follow')
@login_required
def you_follow():
    followers_id = current_user.get_followers_id()

    persons = db.session.query(UsersDB, ProfileDB).select_from(UsersDB). \
        filter(UsersDB.id.in_(followers_id)).join(ProfileDB)

    return render_template('you_follow.html', title='вы подписаны', menu=main_menu, persons=persons,
                           followers=followers_id, me=int(current_user.get_id()))


@profile_blueprint.route('/user_follow/<user_id>')
@login_required
def user_follow(user_id):
    user = UsersDB.query.filter_by(id=user_id).first()

    followers = FollowersDB.query.filter_by(user=user_id).all()
    followers_id = [follower.follower for follower in followers]

    persons = db.session.query(UsersDB, ProfileDB).select_from(UsersDB). \
        filter(UsersDB.id.in_(followers_id)).join(ProfileDB)

    return render_template('you_follow.html', title=f'{user.name} подписан(а)', menu=main_menu, persons=persons,
                           followers=followers_id, me=int(current_user.get_id()), user=user.name)


@profile_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли из акаунта', 'success')
    return redirect(url_for('index'))


@profile_blueprint.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verify_ext(file.filename):
            try:
                img = file.read()
                res = UpdateUserAvatar(img, current_user.get_id())()
                if not res:
                    flash('Ошибка обновления аватара', 'error')
                    return redirect(url_for('profile.profile'))

                flash('Аватар успешно обновлён', 'success')
            except FileNotFoundError as error:
                flash('Ошибка чтения файла', 'error')
                print(f'Ошибка в upload {error}')
        else:
            flash('Ошибка обновления аватара', 'error')

    return redirect(url_for('profile.profile'))


@profile_blueprint.route('/userava')
@login_required
def userava():
    img = ProfileDB.query.filter_by(id=current_user.get_id()).first().avatar

    head = make_response(img)
    head.headers['Content-type'] = 'img/png'

    return head
