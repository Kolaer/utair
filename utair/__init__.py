from flask import Flask, render_template
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.secret_key = "default string, if not set in config"

app.config['MONGODB_SETTINGS'] = {
    'db': 'utair'
}

app.config.from_pyfile('config.py', silent=True)

db = MongoEngine(app)

# db must be created before registering blueprints
# because they use it
from utair.blueprints import auth, user, transaction

app.register_blueprint(auth.bp)
app.register_blueprint(user.bp)
app.register_blueprint(transaction.bp)

# user and transactions generators
if app.env == 'development':
    from utair.blueprints import generator
    app.register_blueprint(generator.bp)

app.add_url_rule('/', endpoint='index')


@app.route('/')
@auth.load_logged_in_user
def index():
    return render_template('index.html')
