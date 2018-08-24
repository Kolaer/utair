Utair test project
==================

Overview
--------

This project has:
 - API for logging in users by sending them token in an email
 - API for users to view their profile
 - API for users to get their bonus transactions (supporting pagination & filtering)
 - API for *special* users to add new bonus transactions
 - Special dev. API for generating fake data and saving it to the database
 - Transaction API example in a form of cli python script

This project assumes that mongodb is running at 127.0.0.1:27017, if not change config.py. For further details see http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/

Install
-------

**Be sure to use the same version of the code as the version of the docs
you're reading.** You probably want the latest tagged version, but the
default Git version is the master branch. ::

    # clone the repository
    git clone https://github.com/kolaer/utair
    cd utair
    # checkout the correct version
    git tag  # shows the tagged versions
    git checkout latest-tag-found-above

Create a virtualenv and activate it::

    python3 -m venv venv
    . venv/bin/activate

Or on Windows cmd::

    py -3 -m venv venv
    venv\Scripts\activate.bat

Install this project::

    pip install -e .

Or, if you want to run transaction API example::

    pip install -e '.[example]'

Run
---

::

    export FLASK_APP=utair
    export FLASK_ENV=development
    flask run

Or on Windows cmd::

    set FLASK_APP=utair
    set FLASK_ENV=development
    flask run

Open http://127.0.0.1:5000 in a browser.

Init db
-------

To initialize database with some users & api users:

Open http://127.0.0.1:5000/gen/generate

It's also possible to add additional users & api users:

Open http://127.0.0.1:5000/gen/generate/user

Open http://127.0.0.1:5000/gen/generate/api_user


API example
-----------

See transaction_api_example.py

Run::

    python3 transaction_api_example.py -h
