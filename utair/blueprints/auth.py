import functools

from flask import Blueprint, g, session, redirect, url_for, request, render_template, flash
from mongoengine import DoesNotExist, MultipleObjectsReturned

from utair.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """Decorator that allows only auth. users."""

    @functools.wraps(view)
    def wrapped(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped


def load_logged_in_user(view):
    """Decorator that load user object from the database
    to ``g.user`` if user's token is in a session."""

    @functools.wraps(view)
    def wrapped(**kwargs):
        token = session.get('token')

        if token is None:
            g.user = None
        else:
            try:
                g.user = User.objects(token=token).get()
            except DoesNotExist:
                return redirect(url_for('auth.login'))
            except MultipleObjectsReturned as e:
                # Shouldn't be possible, because token is unique
                raise e

        return view(**kwargs)

    return wrapped


# Better option would be to add to message queue
def send_token(email, token):
    from utair import app
    if app.config['ENV'] == 'development':
        print('{}: {}'.format(email, token))
    else:
        # Probably store smtp client to reuse it
        import smtplib
        from email.mime.text import MIMEText

        msg = MIMEText("Your token is {}.\n\nGo to login page and enter it or use it in API.".format(token))
        msg['Subject'] = 'Token'
        smtp_login = app.config['SMTP_LOGIN']
        msg['From'] = smtp_login
        msg['To'] = email

        s = smtplib.SMTP(app.config['SMTP_SERVER'])
        s.sendmail(smtp_login, [email], msg.as_string())
        s.quit()


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Sends a token in e-mail to user."""
    if request.method == 'POST':
        email = request.form['email']

        try:
            user = User.objects(email=email).get()
        except DoesNotExist:
            flash("User doesn't exist", 'error')
            return redirect(url_for('auth.login'))
        except MultipleObjectsReturned as e:
            # Shouldn't be possible, because email is unique
            raise e

        # use uuid so bruteforce is useless
        from uuid import uuid4
        token = str(uuid4())

        send_token(email, token)

        user.token = token
        user.save()

        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@bp.route('/token', methods=['POST'])
def save_token():
    """Saves user token in to the session."""
    token = request.form['token']

    session['token'] = token

    return redirect(url_for('index'))


@bp.route('/logout')
def logout():
    """Clear current session, including user token."""
    session.clear()
    return redirect(url_for('index'))
