Ontime
==============

Schedule your tweet to be posted at certain times.

The app is composed of a Flask frontend and a Celery backend; for the database and message queue, I used Postgres and RabbitMQ, but really any will do.

You'll need to supply a `config.py` file:

```
SECRET_KEY = 'this secret key is a required filed for flask apps'
TWITTER_CONSUMER_KEY = 'get this and the next field from twitter'
TWITTER_CONSUMER_SECRET = 'see above'
DEBUG = True
SQLALCHEMY_DATABASE_URI = 'postgres:///database_name'
```

Then, run the following to start everything:

```
python ontime.py
celery -A tasks worker
```
