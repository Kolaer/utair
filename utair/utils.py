from flask import jsonify


def json_ok(data=None):
    res = {'status': 'ok'}

    if data is not None:
        res.update(data)

    return jsonify(res)


def json_error(msg=None):
    res = {'status': 'error'}

    if msg is not None:
        res['msg'] = msg

    return jsonify(res)
