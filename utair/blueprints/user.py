import functools
from decimal import Decimal

from flask import Blueprint, request, jsonify, g
from mongoengine import DoesNotExist, MultipleObjectsReturned

from utair.models import User, Transaction

import dateutil

from utair.utils import json_ok, json_error

bp = Blueprint('user', __name__, url_prefix='/user')

PAGE_SIZE = 10


def token_required(view):
    """Decorator that check for user token is GET arguments."""

    @functools.wraps(view)
    def wrapped(**kwargs):
        token = None

        if request.method == 'GET':
            token = request.args.get('token')
        elif request.method == 'POST':
            if 'token' in request.form:
                token = request.form['token']

        if token is None:
            return json_error('Token not found in request')

        return view(**kwargs)

    return wrapped


def load_user_by_token(view):
    """Decorator that load user object from the database
    in to ``g.user`` by token."""

    @functools.wraps(view)
    def wrapped(**kwargs):
        token = request.args.get('token')

        try:
            user = User.objects(token=token).get()
        except DoesNotExist:
            return json_error('User not found')
        except MultipleObjectsReturned as e:
            # Shouldn't be possible, because token is unique
            raise e

        g.user = user

        return view(**kwargs)

    return wrapped


@bp.route('/info', methods=['GET'])
@load_user_by_token
@token_required
def user_info():
    user = g.user

    total_bonus = Transaction.objects(card_id=user.card_id).sum('bonus')

    return json_ok({
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'patronymic': user.patronymic,
            'email': user.email,
            'card_id': user.card_id,
            'total_bonus': total_bonus
        }
    })


def add_param(params, arg, key=None, type=None, converter=None):
    """Adds parameter to params map.
    Supports: custom key
              custom type
              converting param before assignment"""
    if key is None:
        key = arg
    if type is None:
        type = str

    param = request.args.get(arg, type=type)

    if param is not None:
        if converter is None:
            params[key] = param
        else:
            params[key] = converter(param)


@bp.route('/transactions', methods=['GET'])
@load_user_by_token
@token_required
def user_transactions():
    """Lets user see his transactions, supports:
    pagination (page param)
    filtering: from (place)
               to (place)
               before (date)
               after (date)
               transaction_ids
               less (bonus)
               more (bonus)"""
    card_id = g.user.card_id

    page = request.args.get('page', default=1, type=int)
    # page is number from 1 to ...
    page = max(1, page)

    params = {'card_id': card_id}

    add_param(params, 'from', 'from_place')

    add_param(params, 'to', 'to_place')

    # must treat this differently, because its list (always not None)
    transaction_ids = request.args.getlist('id', type=int)

    if len(transaction_ids) > 0:
        params['transaction_id__in'] = transaction_ids

    add_param(params, 'before', 'date__lte', converter=dateutil.parser.parse)

    add_param(params, 'after', 'date__gte', converter=dateutil.parser.parse)

    # bonus more than
    add_param(params, 'more', 'bonus__gte', type=Decimal)

    # bonus less than
    add_param(params, 'less', 'bonus__lte', type=Decimal)

    transactions = Transaction.objects(**params).paginate(page=page, per_page=PAGE_SIZE)

    # list of jsoninied transactions
    trans_json = []

    for transaction in transactions.items:
        trans_json.append({
            'transaction_id': transaction.transaction_id,
            'card_id': transaction.card_id,
            'bonus': float(transaction.bonus),
            'from': transaction.from_place,
            'to': transaction.to_place,
            'date': transaction.date
        })

    return json_ok({'transactions': trans_json})
