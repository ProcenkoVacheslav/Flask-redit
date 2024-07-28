from configurations.config import db
from werkzeug.security import generate_password_hash
import datetime

from random import seed, randint
import forgery_py
from sqlalchemy.exc import IntegrityError


class UsersDB(db.Model):
    __tablename__ = "users_db"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(500), nullable=False)
    date = db.Column(db.Date, default=datetime.date.today())

    profile = db.relationship('ProfileDB', backref='users_db', uselist=False)
    channel_information = db.relationship('ChannelInformationDB', backref='users_db', uselist=False)
    post = db.relationship('PostsDB', backref='users_db', uselist=False)
    likes = db.relationship('LikesDB', backref='users_db', uselist=False)

    @staticmethod
    def generate_fake(count):
        seed()

        for user in range(count):
            new_user = UsersDB(name=forgery_py.name.first_name(),
                               email=forgery_py.internet.email_address(),
                               password=generate_password_hash('56gt32'))

            db.session.add(new_user)

            try:
                db.session.commit()
            except IntegrityError:
                print('asd')
                db.session.rollback()

    def __repr__(self):
        return f'{__class__.__name__} id: {self.id}'


class ProfileDB(db.Model):
    __tablename__ = "profile_db"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('users_db.id'))
    avatar = db.Column(db.BLOB)
    name = db.Column(db.String(20), default='нет', nullable=False)
    sure_name = db.Column(db.String(20), default='нет', nullable=False)
    age = db.Column(db.Integer, default=18, nullable=False)
    gender = db.Column(db.String(20), default='нет', nullable=False)
    city = db.Column(db.String(20), default='нет', nullable=False)
    about_yourself = db.Column(db.Text, default='нет информации', nullable=False)

    likes = db.relationship('LikesDB', backref='profile_db', uselist=False)

    @staticmethod
    def generate_fake(count):
        seed()

        for profile in range(count):
            new_profile = ProfileDB(profile_id=profile + 1)
            db.session.add(new_profile)
            db.session.commit()

    def __repr__(self):
        return f'{__class__.__name__} id: {self.id}'


class ChannelInformationDB(db.Model):
    __tablename__ = "channel_information_db"

    id = db.Column(db.Integer, primary_key=True)
    channel_information_id = db.Column(db.Integer, db.ForeignKey('users_db.id'))
    followers = db.Column(db.Integer, default=0)
    you_follow = db.Column(db.Integer, default=0)
    channel_information = db.Column(db.Text)

    @staticmethod
    def generate_fake(count):
        seed()

        for channel_information in range(count):
            new_channel_information = ChannelInformationDB(channel_information_id=channel_information + 1)
            db.session.add(new_channel_information)
            db.session.commit()

    def __repr__(self):
        return f'{__class__.__name__} {self.id}'


class PostsDB(db.Model):
    __tablename__ = "posts_db"

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer, db.ForeignKey('users_db.id'))
    title = db.Column(db.String(50))
    main = db.Column(db.Text)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    fake_date = db.Column(db.String(50), default=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    date = db.Column(db.DateTime, default=datetime.datetime.now())

    comment = db.relationship('CommentsDB', backref='posts_db', uselist=False)
    likes_rel = db.relationship('LikesDB', backref='posts_db', uselist=False)

    @staticmethod
    def generate_fake(count):
        seed()

        user_count = UsersDB.query.count()

        for post in range(count):
            user = randint(1, user_count)
            new_post = PostsDB(author=user,
                               title=forgery_py.lorem_ipsum.title(randint(1, 3)),
                               main=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                               fake_date=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                               date=datetime.datetime.now())
            db.session.add(new_post)
            db.session.commit()

    @staticmethod
    def set_comments():
        post_count = PostsDB.query.count()

        for post in range(1, post_count + 1):
            comments = CommentsDB.query.filter_by(post_id=post).count()

            new_post = PostsDB.query.filter_by(id=post).update({'comments': comments})

            assert new_post is not None, 'что-то не так в set_comments'

            db.session.commit()

    def __repr__(self):
        return f'{__class__.__name__} id: {self.id}'


class CommentsDB(db.Model):
    __tablename__ = "comments_db"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts_db.id'))
    fake_date = db.Column(db.String(50), default=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"))
    date = db.Column(db.DateTime, default=datetime.datetime.now())
    author = db.Column(db.Integer, db.ForeignKey('users_db.id'))
    comment = db.Column(db.Text)

    @staticmethod
    def generate_fake(count):
        seed()

        user_count = UsersDB.query.count()
        post_count = PostsDB.query.count()

        for post in range(count):
            user = randint(1, user_count)
            post = randint(1, post_count)

            new_comment = CommentsDB(author=user,
                                     post_id=post,
                                     fake_date=datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                                     date=datetime.datetime.now(),
                                     comment=forgery_py.lorem_ipsum.sentences(randint(3, 5)))

            db.session.add(new_comment)
            db.session.commit()

    def __repr__(self):
        return f'{__class__.__name__} id: {self.id}'


class FollowersDB(db.Model):
    __tablename__ = "followers_db"

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users_db.id'))
    follower = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return f'{__class__.__name__} id: {self.id}'


class LikesDB(db.Model):
    __tablename__ = "likes_db"

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts_db.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users_db.id'))
    profile_id = db.Column(db.Integer, db.ForeignKey('profile_db.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.now())

    def __repr__(self):
        return f'{__class__.__name__} id: {self.id}'
