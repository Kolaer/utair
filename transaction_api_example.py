import argparse
from decimal import Decimal

import requests


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t',
                        '--token',
                        type=str,
                        required=True,
                        help='Api user token')
    parser.add_argument('-c',
                        '--card_id',
                        type=int,
                        required=True,
                        help='User card id')
    parser.add_argument('-d',
                        '--date',
                        type=str,
                        required=True,
                        help='Transaction\'s date')
    parser.add_argument('-f',
                        '--from',
                        dest='from_place',
                        type=str,
                        required=True,
                        help='Flight\'s point of departure')
    parser.add_argument('-to',
                        '--to',
                        type=str,
                        required=True,
                        help='Flight\'s point of destination')
    parser.add_argument('-b',
                        '--bonus',
                        type=Decimal,
                        required=True,
                        help='User\' bonus')
    parser.add_argument('-tid',
                        '--transaction_id',
                        type=int,
                        required=True,
                        help='Transaction id')
    parser.add_argument('-u',
                        '--url',
                        type=str,
                        required=False,
                        default="http://127.0.0.1:5000",
                        help='Api URL')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    payload = {
        'token': args.token,
        'from': args.from_place,  # from is a keyword
        'to': args.to,
        'bonus': str(args.bonus),  # convert from decimal to string
        'card_id': args.card_id,
        'transaction_id': args.transaction_id,
        'date': args.date,
    }

    response = requests.post(args.url + '/transaction/add', data=payload)

    print(response.text)
