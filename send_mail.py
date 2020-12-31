import json
import time
import requests
import threading

from flask import Flask
from flask import request
from flask import render_template


app = Flask(__name__)


# Configure this.
FROM_EMAIL_ADDR = 'mail@yourdomain.de'
TO_EMAIL_ADDR = 'mail@otherdomain.de'
REDIRECT_URL = 'http://127.0.0.1:5000/callback/'
CLIENT_ID = ''
CLIENT_SECRET = ''
BASE_OAUTH_API_URL = 'https://accounts.zoho.eu/'
BASE_API_URL = 'https://mail.zoho.eu/api/'

ZOHO_DATA = {
    "access_token": "",
    "refresh_token": "",
    "api_domain": "https://www.zohoapis.eu",
    "token_type": "Bearer",
    "expires_in": 3600,
    "account_id": ""
}


def req_zoho():
    url = (
        "%soauth/v2/auth?"
        "scope=ZohoMail.messages.CREATE,ZohoMail.accounts.READ&"
        "client_id=%s&"
        "response_type=code&"
        "access_type=offline&"
        "redirect_uri=%s"
    ) % (BASE_OAUTH_API_URL, CLIENT_ID, REDIRECT_URL)
    print('CLICK THE LINK:')
    print(url)
    print('This only has to be done once.')


def get_access_token(code):
    state = request.args.get('state')
    url = '%soauth/v2/token' % BASE_OAUTH_API_URL
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URL,
        'scope': 'ZohoMail.messages.CREATE,ZohoMail.accounts.READ',
        'grant_type': 'authorization_code',
        'state': state
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    r = requests.post(url, data=data, headers=headers)
    data = json.loads(r.text)
    ZOHO_DATA['access_token'] = data['access_token']


def get_account_id():
    url = BASE_API_URL + 'accounts'
    headers = {
        'Authorization': 'Zoho-oauthtoken ' + ZOHO_DATA['access_token']
    }
    r = requests.get(url, headers=headers)
    data = json.loads(r.text)
    ZOHO_DATA['account_id'] = data['data'][0]['accountId']


def send_mail(body, email_address):
    url = BASE_API_URL + 'accounts/%s/messages'
    url = url % ZOHO_DATA['account_id']
    data = {
       "fromAddress": FROM_EMAIL_ADDR,
       "toAddress": email_address,
       "ccAddress": "",
       "bccAddress": "",
       "subject": "Test E-Mail",
       "content": body,
       "askReceipt": "no"
    }
    headers = {
        'Authorization': 'Zoho-oauthtoken ' + ZOHO_DATA['access_token']
    }
    r = requests.post(url, headers=headers, json=data)
    print(r.text)


def refresh_auth():
    # Update the access token every 50 minutes using the refresh token.
    # The access token is valid for exactly 1 hour.
    time.sleep(10)
    while True:
        url = (
            '%soauth/v2/token?'
            'refresh_token=%s&'
            'client_id=%s&'
            'client_secret=%s&'
            'grant_type=refresh_token'
        ) % (BASE_OAUTH_API_URL, ZOHO_DATA['refresh_token'], CLIENT_ID, CLIENT_SECRET)
        r = requests.post(url)
        data = json.loads(r.text)
        if 'access_token' in data:
            ZOHO_DATA['access_token'] = data['access_token']
            print('refreshed', ZOHO_DATA)
            time.sleep(3000)  # 50 minutes
        else:
            # Retry after 1 minute
            time.sleep(60)


@app.route('/callback/', methods=['GET', 'POST'])
def zoho_callback_route():
    code = request.args.get('code', None)
    if code is not None:
        get_access_token(code)
        get_account_id()
    return 'OK', 200


@app.route('/sendmail/', methods=['GET', 'POST'])
def send_mail_route():
    # Send a HTML email!
    data = ['1', '2', '3']
    mail = render_template('mail_template.j2', data=data)
    send_mail(mail, TO_EMAIL_ADDR)
    return 'OK', 200


def main():
    req_zoho()
    t = threading.Thread(target=refresh_auth)
    t.start()
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
