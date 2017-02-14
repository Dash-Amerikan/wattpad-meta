

"""
Download metadata about Wattpad stories that match a set of searches.
"""


from flask import Flask, redirect, request, url_for
from flask_oauth import OAuth
import json
import os
import urllib
import urlparse


app = Flask(__name__)

oauth = OAuth()
wattpad = oauth.remote_app(
    'wattpad',
    base_url='https://www.wattpad.com/',
    request_token_url='https://api.wattpad.com/v4/auth/token?grantType=authorizationCode',
    access_token_url='https://api.wattpad.com/v4/auth/token?grantType=authorizationCode',
    authorize_url='https://www.wattpad.com/oauth/code',
    consumer_key=os.getenv('WATTPAD_API_KEY'),
    consumer_secret=os.getenv('WATTPAD_SECRET'),
    )


LOGIN_INFO_FILE = 'login.json'
LOGIN_INFO = {}


@app.route('/')
def root():
    global LOGIN_INFO

    if os.path.exists(LOGIN_INFO_FILE):
        with open(LOGIN_INFO_FILE) as file_in:
            LOGIN_INFO = json.load(file_in)
        return redirect(url_for('search'))

    else:
        return redirect(url_for('login'))


@app.route('/login/')
def login():
    url = 'https://www.wattpad.com/oauth/code'
    params = {
        'api_key': os.getenv('WATTPAD_API_KEY'),
        'scope': 'read',
        'redirect_uri': 'http://localhost:5000/login/done',
        }
    print(url + '?' + urllib.urlencode(params))
    return redirect(url + '?' + urllib.urlencode(params))


@app.route('/login/done')
def login_done():
    print('code', request.args.get('code'))
    print('error', request.args.get('error'))
    return 'code: {}\nerror: {}\n'.format(request.args.get('code'), request.args.get('error'))


@app.route('/search/')
def search():
    pass


@app.route('/output/')
def output():
    pass


if __name__ == '__main__':
    app.run()
