

"""
Download metadata about Wattpad stories that match a set of searches.
"""


import csv
import cStringIO as StringIO
from flask import Flask, redirect, render_template, request, url_for
import json
import os
import requests
import urllib
import urlparse


app = Flask(__name__)


LOGIN_INFO_FILE = 'login.json'
LOGIN_INFO = None


def read_login_info():
    """Read the login information and set the global LOGIN_INFO."""
    global LOGIN_INFO

    if LOGIN_INFO is None and os.path.exists(LOGIN_INFO_FILE):
        with open(LOGIN_INFO_FILE) as file_in:
            LOGIN_INFO = json.load(file_in)

    return LOGIN_INFO


@app.route('/')
def root():
    login_info = read_login_info()
    if login_info is not None:
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
    login_info = read_login_info()
    tags = request.args.get('tags', '').splitlines()

    index = {}
    for tag in tags:
        params = {
            'query': tag,
            'limit': 1000,
            'mature': 0,
            }
        headers = {
            'Authorization': os.getenv('WATTPAD_API_KEY'),
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3004.3 Safari/537.36',
            }
        r = requests.get('https://api.wattpad.com:443/v4/stories', params=params, headers=headers)
        for story in r.json()['stories']:
            index[story['id']] = story

    io = StringIO.StringIO()
    writer = csv.writer(io)
    writer.writerow(['title', 'url', 'description', 'tags', 'user', 'readCount', 'voteCount',
                     'createDate', 'categories'])
    for story in index.values():
        writer.writerow([
            story['title'].encode('utf8'),
            story['url'].encode('utf8'),
            story['description'].encode('utf8'),
            story['tags'].encode('utf8'),
            story['user'].encode('utf8'),
            story['readCount'],
            story['voteCount'],
            story['createDate'].encode('utf8'),
            ' '.join(str(cat) for cat in story['categories']),
            ])

    # TODO: it would be really nice to show some progress as we're querying wattpad
    return (io.getvalue(), {'Content-Type': 'text/csv'})


if __name__ == '__main__':
    app.run()
