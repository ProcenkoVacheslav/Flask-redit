from flask_login import UserMixin
from configurations.config import db as dbase
from configurations.models import ProfileDB, FollowersDB, LikesDB

import sqlite3


class UserLogin(UserMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__user = None

    def from_db(self, user_id, db):
        try:
            self.__user = db.query.filter_by(id=user_id).first()
        except Exception as error:
            print(f'Произошла ошибка в from_db {error}')

        return self

    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user.id)

    @staticmethod
    def verify_ext(filename):
        ext = filename.rsplit('.', 1)[1]
        if ext in ['png', 'jpg']:
            return True
        return False

    def get_followers_id(self):
        followers = FollowersDB.query.filter_by(user=self.get_id()).all()
        followers_id = [follower.follower for follower in followers]

        return followers_id

    def get_likes_id(self):
        likes = LikesDB.query.filter_by(user_id=self.get_id()).all()
        likes_id = [like.post_id for like in likes]

        return likes_id


class UpdateUserAvatar:
    def __init__(self, img, id_):
        self.img = img
        self.id = id_

    def __call__(self, *args, **kwargs):
        if not self.img:
            return False

        try:
            binary = sqlite3.Binary(self.img)

            try:
                profile_db = ProfileDB.query.filter_by(profile_id=self.id).update({'avatar': binary})
                dbase.session.commit()

                assert profile_db is not None, 'profile_db is None'

                return True
            except Exception as error:
                profile_db = ProfileDB(profile_id=self.id, avatar=binary)
                dbase.session.add(profile_db)
                dbase.session.commit()
                print(error)
                return True

        except Exception as error:
            print(f'Ошибка в update_user_avatar {error}')
            return False
