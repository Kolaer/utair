import functools

from flask import Blueprint, request, jsonify, g
from mongoengine import DoesNotExist, MultipleObjectsReturned

from utair.models import User, Transaction

import dateutil

bp = Blueprint('user', __name__, url_prefix='/user')

PAGE_SIZE = 10


def token_required(view):
    """Decorator that check for user token is GET arguments."""

    @functools.wraps(view)
    def wrapped(**kwargs):
        if request.method == 'GET':
            token = request.args.get('token')

            if token is None:
                return jsonify({
                    'status': 'error',
                    'message': 'Token not found in request'
                })

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
            return jsonify({
                'status': 'error',
                'message': 'User not found'
            })
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

    return jsonify({
        'status': 'ok',
        'user': {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'patronymic': user.patronymic,
            'email': user.email,
            'card_id': user.card_id,
            'total_bonus': total_bonus
        }
    })


@bp.route('/transactions', methods=['GET'])
@load_user_by_token
@token_required
def user_transactions():
    card_id = g.user.card_id

    page = request.args.get('page', default=1, type=int)
    # page is number from 1 to ...
    page = max(1, page)

    params = {'card_id': card_id}

    from_place = request.args.get('from')

    if from_place is not None:
        params['from_place'] = from_place

    to_place = request.args.get('to')

    if to_place is not None:
        params['to_place'] = to_place

    transaction_ids = request.args.getlist('id', type=int)

    if len(transaction_ids) > 0:
        params['transaction_id__in'] = transaction_ids

    before = request.args.get('before')

    if before is not None:
        params['date__lte'] = dateutil.parser.parse(before)

    after = request.args.get('after')

    if after is not None:
        params['date__gte'] = dateutil.parser.parse(after)

    # bonus more than
    more = request.args.get('more', type=float)

    if more is not None:
        params['bonus__gte'] = more

    # bonus less than
    less = request.args.get('less', type=float)

    if less is not None:
        params['bonus__lte'] = less

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

    return jsonify({
        'status': 'ok',
        'transactions': trans_json
    })
