import functools
from decimal import Decimal

import dateutil
from flask import Blueprint, request, jsonify

from utair.models import Transaction, ApiUser

bp = Blueprint('transaction', __name__, url_prefix='/transaction')


def api_user_required(view):
    """Decorator that requires api user token."""

    @functools.wraps(view)
    def wrapped(**kwargs):
        token = None
        if request.method == 'POST':
            if 'token' in request.form:
                token = request.form['token']
        elif request.method == 'GET':
            token = request.args.get('token')

        if token is None:
            return jsonify({
                'status': 'error',
                'message': 'You must specify api user token'
            })

        if ApiUser.objects(token=token).limit(1).count() != 1:
            return jsonify({
                'status': 'error',
                'message': 'Api user not found'
            })

        return view(**kwargs)

    return wrapped


@bp.route('/add', methods=['POST'])
@api_user_required
def add_transaction():
    card_id = int(request.form['card_id'])
    transaction_id = int(request.form['transaction_id'])

    if Transaction.objects(transaction_id=transaction_id).limit(1).count() != 0:
        # transaction already exists
        return jsonify({
            'status': 'error',
            'message': 'Transaction with that id already exist'
        })

    bonus = Decimal(request.form['bonus'])

    from_place = request.form['from']
    to_place = request.form['to']

    date = dateutil.parser.parse(request.form['date'])

    transaction = Transaction(transaction_id=transaction_id,
                              card_id=card_id,
                              bonus=bonus,
                              from_place=from_place,
                              to_place=to_place,
                              date=date)

    transaction.save()

    return jsonify({
        'status': 'ok'
    })
