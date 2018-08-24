import random

from flask import Blueprint

from utair import db, app
from utair.models import User, ApiUser
from utair.utils import json_ok

bp = Blueprint('gen', __name__, url_prefix='/gen')

ALPHABET = list('qwertyuiopasdfghjklzxcvbnm')


def generate_word():
    length = random.randint(3, 10)
    return ''.join(random.choices(ALPHABET, k=length))


def generate_id():
    return random.randint(10 ** 6, 10 ** 7 - 1)


def generate_token():
    from uuid import uuid4
    return str(uuid4())


def generate_user():
    user = User(first_name=generate_word(),
                last_name=generate_word(),
                patronymic=generate_word(),
                email=generate_word() + '@' + generate_word() + '.' + generate_word(),
                card_id=generate_id())

    user.save()


@bp.route('/generate/user')
def generate_user_web():
    generate_user()

    return json_ok()


def generate_api_user():
    api_user = ApiUser(token=generate_token())
    api_user.save()


@bp.route('/generate/api_user')
def generate_api_user_web():
    generate_api_user()

    return json_ok()


@bp.route('/generate')
def generate():
    """Clears current database and generates new database."""
    db.connection.drop_database(app.config['MONGODB_DB'])

    for _ in range(100):
        generate_user()

    for _ in range(10):
        generate_api_user()

    return json_ok()
