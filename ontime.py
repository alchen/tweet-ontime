import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.oauth import OAuth
from flask.ext.seasurf import SeaSurf
try:
    import gevent
    from gevent.monkey import patch_all
    patch_all()
    from psycogreen.gevent import patch_psycopg
    patch_psycopg()
except:
    pass

app = Flask(__name__)

app.config.from_pyfile('config.py')

csrf = SeaSurf(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.setup_app(app)

oauth = OAuth()
twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=app.config['TWITTER_CONSUMER_KEY'],
    consumer_secret=app.config['TWITTER_CONSUMER_SECRET']
)

from views import *

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
