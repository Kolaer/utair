from utair import db


class User(db.Document):
    first_name = db.StringField(max_length=50, required=True)
    last_name = db.StringField(max_length=50, required=True)
    patronymic = db.StringField(max_length=50)

    email = db.EmailField(required=True, unique=True)

    card_id = db.LongField(min_value=0, required=True, unique=True)

    token = db.StringField()

    meta = {
        'indexes': [
            'email',
            'card_id',
            {
                'fields': ['token'],
                'unique': True,
                'sparse': True
             }
        ]
    }


class Transaction(db.Document):
    # probable use _id? ; but maybe it's coming from external source?
    transaction_id = db.LongField(min_value=0, required=True, unique=True)
    # maybe replace with reference to user?
    card_id = db.LongField(min_value=0, required=True)

    # floats/doubles have precision errors
    bonus = db.DecimalField(min_value=0, precision=2, required=True)

    # from is a keyword, so...
    from_place = db.StringField(required=True)
    to_place = db.StringField(required=True)

    date = db.DateTimeField(required=True)

    meta = {
        'indexes': [
            'transaction_id',
            'card_id'
        ]
    }


class ApiUser(db.Document):
    token = db.StringField(required=True, unique=True)

    meta = {
        'indexes': [
            'token'
        ]
    }
