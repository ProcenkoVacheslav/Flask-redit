from flask import Blueprint

from flask import flash, url_for, render_template, redirect, request, current_app, make_response
from flask_login import login_required, current_user

from configurations.settings import main_menu
from configurations.config import db
from configurations.forms import AddPostForm, SetCommentForm
from configurations.models import UsersDB, PostsDB, ProfileDB, LikesDB, FollowersDB, ChannelInformationDB, CommentsDB

import datetime

post_blueprint = Blueprint('post', __name__, template_folder='configurations/templates',
                           static_folder='configurations/static')


@post_blueprint.route('/', methods=['GET', 'POST'])
@login_required
def posts():
    page = request.args.get('page', 1, type=int)

    likes_id = current_user.get_likes_id()
    followers_id = current_user.get_followers_id()

    pagination = db.session.query(PostsDB, UsersDB, ProfileDB).select_from(PostsDB).join(UsersDB).join(ProfileDB). \
        order_by(PostsDB.date.desc()).paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'],
                                               error_out=False)

    this_posts = pagination.items

    datas = {
        'title': 'посты',
        'menu': main_menu,
        'posts': this_posts,
        'pagination': pagination,
        'likes': likes_id,
        'followers': followers_id,
        'me': int(current_user.get_id()),
    }

    return render_template('posts.html', **datas)


@post_blueprint.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = AddPostForm()

    if form.validate_on_submit():
        post = {
            'title': form.title.data,
            'main': form.main.data,
            'author': current_user.get_id(),
        }

        try:
            new_post = PostsDB(**post)
            db.session.add(new_post)
            db.session.commit()
            flash('Запись успешно добавлена', 'success')
            return redirect(url_for('post.posts'))
        except Exception as error:
            print(f'Произошла ошибка в add_post {error}')
            flash('Произошла ошибка', 'error')

    return render_template('add_post.html', title='посты', menu=main_menu, form=form)


@post_blueprint.route('/likes_this_post/<id_>')
@login_required
def likes_this_post(id_):
    followers_id = current_user.get_followers_id()

    persons = db.session.query(LikesDB, UsersDB, ProfileDB).select_from(LikesDB).filter_by(
        post_id=id_).join(ProfileDB).join(UsersDB).order_by(LikesDB.date.desc())

    return render_template('like_this_posts.html', title='понравилось', menu=main_menu, persons=persons, cur_post=id_,
                           followers=followers_id, me=int(current_user.get_id()))


@post_blueprint.route('/you_follower')
@login_required
def you_follower():
    likes_id = current_user.get_likes_id()
    followers_id = current_user.get_followers_id()

    page = request.args.get('page', 1, type=int)

    pagination = db.session.query(PostsDB, UsersDB, ProfileDB).select_from(PostsDB).filter(
        PostsDB.author.in_(followers_id)).join(UsersDB).join(ProfileDB).order_by(PostsDB.date.desc()). \
        paginate(page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

    followers_posts = pagination.items

    datas = {
        'title': 'подписки',
        'menu': main_menu,
        'posts': followers_posts,
        'pagination': pagination,
        'likes': likes_id,
        'followers': followers_id,
        'me': int(current_user.get_id()),
    }

    return render_template('you_follower.html', **datas)


@post_blueprint.route('/comments/<post_id>', methods=['GET', 'POST'])
@login_required
def comments(post_id):
    form = SetCommentForm()

    all_comments = db.session.query(CommentsDB, UsersDB, ProfileDB).select_from(CommentsDB).filter_by(
        post_id=post_id).join(UsersDB).join(ProfileDB).order_by(CommentsDB.date.desc())

    if form.validate_on_submit():
        comment = CommentsDB(post_id=post_id,
                             fake_date=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                             date=datetime.datetime.now(),
                             author=current_user.get_id(),
                             comment=form.comment.data,
                             )

        try:
            db.session.add(comment)
            db.session.commit()
        except Exception as error:
            flash('Что-то пошло не так, попробуйте снова.', 'error')
            print(f'Произошла ошибка в comments {error}')

        post = PostsDB.query.filter_by(id=post_id).first()

        new_post = PostsDB.query.filter_by(id=post_id).update({'comments': post.comments + 1})

        assert new_post is not None, 'что-то не так в comments'

        db.session.commit()

        form.comment.data = ''

        flash('Комментарий успешно добавлен.', 'success')

    return render_template('comments.html', menu=main_menu, title='комметарии', form=form, comments=all_comments,
                           post_id=post_id, me=int(current_user.get_id()))


@post_blueprint.route('/userava/<id_>')
@login_required
def avatar_userava(id_):
    img = ProfileDB.query.filter_by(profile_id=id_).first().avatar

    if img:
        head = make_response(img)
        head.headers['Content-type'] = 'img/png'

        return head
    else:
        return False


@post_blueprint.route('/set_like/<post_id>/<cur>/<following>')
@login_required
def set_like(post_id, cur, following):
    post = PostsDB.query.filter_by(id=post_id).first()

    cur_likes = post.likes

    new_post = PostsDB.query.filter_by(id=post_id).update({'likes': cur_likes + 1})

    assert new_post is not None, 'Что-то не так в set_like'

    db.session.commit()

    like = LikesDB(post_id=post_id,
                   user_id=current_user.get_id(),
                   profile_id=current_user.get_id())

    try:
        db.session.add(like)
        db.session.commit()
    except Exception as error:
        print(f'Произошла ошибка в set_like {error}')
        db.session.rollback()

    if following == '0':
        return redirect(f'/posts/you_follower?page={cur}')
    else:
        return redirect(f'/posts/?page={cur}')


def main_part_of_follow(author):
    channel = ChannelInformationDB.query.filter_by(id=current_user.get_id()).first()
    follower_channel = ChannelInformationDB.query.filter_by(id=author).first()

    follow = FollowersDB(user=current_user.get_id(),
                         follower=author)

    new_channel = ChannelInformationDB.query.filter_by(id=current_user.get_id()). \
        update({'you_follow': channel.you_follow + 1})
    new_user_channel = ChannelInformationDB.query.filter_by(id=author). \
        update({'followers': follower_channel.followers + 1})

    assert new_channel is not None, 'Что-то не так в main_part_of_follow'
    assert new_user_channel is not None, 'Что-то не так в main_part_of_follow'

    db.session.commit()

    try:
        db.session.add(follow)
        db.session.commit()
    except Exception as error:
        print(f'Произошла ошибка в set_follow {error}')
        db.session.rollback()


@post_blueprint.route('/follow/<post_id>/<page>')
@login_required
def set_follow(post_id, page):
    post = PostsDB.query.filter_by(id=post_id).first()

    author = post.author

    main_part_of_follow(author)

    return redirect(f'/posts/?page={page}')


@post_blueprint.route('/follow_this_likes/<user>/<post_id>')
@login_required
def set_follow_this_likes(user, post_id):
    author = user

    main_part_of_follow(author)

    return redirect(f'/posts/likes_this_post/{post_id}')


@post_blueprint.route('/follow_like_posts/<post_id>')
@login_required
def set_follow_like_posts(post_id):
    post = PostsDB.query.filter_by(id=post_id).first()

    author = post.author

    main_part_of_follow(author)

    return redirect(f'/profile/like_posts')


@post_blueprint.route('/follow_follow_you/<post_id>')
@login_required
def set_follow_follow_you(post_id):
    author = post_id

    main_part_of_follow(author)

    return redirect('/profile/follow_you')
