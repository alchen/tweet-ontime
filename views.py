import tasks
import pytz
from datetime import datetime
from dateutil import parser
from ontime import app, twitter, db, login_manager
from flask import render_template, request, flash, redirect, url_for
from flask.ext.login import login_required, login_user, logout_user
from flask.ext.login import current_user


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(24), unique=True, nullable=False)
    oauth_token = db.Column(db.String(200), nullable=False)
    oauth_secret = db.Column(db.String(200), nullable=False)

    def get_id(self):
        return self.id

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def __repr__(self):
        return '<User %r>' % self.name


@app.route('/')
def show_index():
    if current_user.is_authenticated():
        return render_template('tweet.html')
    else:
        return render_template('prompt.html')


@app.route('/schedule', methods=['POST'])
def schedule():
    date_str = (request.form['date'] + ' ' +
                request.form['time'] +
                request.form['ampm'] + ' ' +
                request.form['timezone'])
    eta = parser.parse(date_str)
    countdown = (eta.astimezone(pytz.utc) - datetime.now(pytz.utc)).\
        total_seconds()
    tasks.update.apply_async(
        args=[get_twitter_token(), request.form['status']],
        countdown=countdown
    )
    return redirect('/')


@login_manager.user_loader
def load_user(id):
    return Users.query.get(id)


@twitter.tokengetter
def get_twitter_token():
    if current_user.is_authenticated():
        return (current_user.oauth_token, current_user.oauth_secret)
    else:
        return None


@app.route('/login')
def login():
    if current_user.is_authenticated():
        return redirect('/')
    else:
        return twitter.authorize(
            callback=url_for(
                'oauth_authorized',
                next=request.args.get('next') or request.referrer or None
            )
        )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash('You are denied the request to sign in.')
        return redirect(next_url)

    this_account = Users.query.filter_by(name=resp['screen_name']).first()
    if this_account is None:
        new_account = Users(
            name=resp['screen_name'],
            oauth_token=resp['oauth_token'],
            oauth_secret=resp['oauth_token_secret']
        )
        db.session.add(new_account)
        db.session.commit()
        this_account = new_account
    else:
        this_account.name = resp['screen_name']
        this_account.oauth_token = resp['oauth_token']
        this_account.oauth_secret = resp['oauth_token_secret']
        db.session.commit()

    login_user(this_account)

    flash('You are now signed in as %s' % resp['screen_name'])
    return redirect(next_url)

db.create_all()
