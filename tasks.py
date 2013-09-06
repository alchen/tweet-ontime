import config
from celery import Celery
from flask_oauth import OAuth

celery = Celery('ontime', broker='amqp://')

oauth = OAuth()
twitter = oauth.remote_app(
    'twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authorize',
    consumer_key=config.TWITTER_CONSUMER_KEY,
    consumer_secret=config.TWITTER_CONSUMER_SECRET
)


@twitter.tokengetter
def get_twitter_token(token=None):
    return token


@celery.task(ignore_result=True)
def update(user_id, oauth_token, status):
    twitter.post('statuses/update.json', data={'status': status},
                 token=oauth_token)
    return
