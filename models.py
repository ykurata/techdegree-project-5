import datetime
import re

from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from slugify import slugify
from peewee import *


DATABASE = SqliteDatabase('journal.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)


    @classmethod
    def create_user(cls, username, password, admin=False):
        try:
            cls.create(
                username=username,
                password=generate_password_hash(password),
                is_admin=admin
            )
        except IntegrityError:
            ValueError("User already exists.")


class Entry(Model):
    user = ForeignKeyField(User)
    title = CharField()
    slug = CharField(unique=True)
    timestamp = DateTimeField(default= datetime.datetime.now)
    time_spent = IntegerField()
    content = TextField()
    resources = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)

    def save(self, *args, **kwargs):
        self.slug = re.sub('[^\w]+', '-', self.title.lower())
        super(Entry, self).save(*args, **kwargs)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry], safe=True)
    DATABASE.close()
