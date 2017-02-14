

"""
Download metadata about Wattpad stories that match a set of searches.
"""


from flask import Flask, redirect, render_template, request, url_for
import json
import os
import requests
import urllib
import urlparse


app = Flask(__name__)


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
    code = request.args.get('code')
    error = request.args.get('error')
    print('code', code)
    print('error', error)

    if code:
        resp = requests.post(
            'https://api.wattpad.com/v4/auth/token?grantType=authorizationCode',
            data={
                'apiKey': os.getenv('WATTPAD_API_KEY'),
                'secret': os.getenv('WATTPAD_SECRET'),
                'authCode': code,
                'redirectUri': 'http://localhost:5000/login/done',
            })
        login_info = resp.json()
        print(login_info)
        with open(LOGIN_INFO_FILE, 'w') as file_out:
            json.dump(login_info, file_out)
        return redirect(url_for('search'))

    elif error:
        return '<strong><font color=red>ERROR: {}</font></strong>'.format(error)

    else:
        return 'thank you'


@app.route('/search/')
def search():
    return render_template('search.html')


@app.route('/output/')
def output():
    pass


if __name__ == '__main__':
    app.run()
