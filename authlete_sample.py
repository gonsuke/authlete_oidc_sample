#!/usr/bin/env python3

import sys
import requests
from requests.auth import HTTPBasicAuth
import urllib.parse
from pprint import pprint

CLIENT_ID = 'CLIENT_ID'
SERVICE_API_KEY = 'SERVICE_API_KEY'
SERVICE_API_SECRET = 'SERVICE_API_SECRET'
AUTHORIZATION_ENDPOINT = 'https://api.authlete.com/api/auth/authorization'
AUTHORIZATION_ISSUE_ENDPOINT = 'https://api.authlete.com/api/auth/authorization/issue'
TOKEN_ENDPOINT = 'https://api.authlete.com/api/auth/token'
USER_INFO_ENDPOINT = 'https://api.authlete.com/api/auth/userinfo'
REDIRECT_URI = 'https://api.authlete.com/api/mock/redirection/{}'.format(
    SERVICE_API_KEY)


def authorization():
    print('Accessing authorization api...')
    authorization_payload = {
        'parameters': 'response_type=code&scope=openid&client_id={}&redirect_uri={}'.format(CLIENT_ID, urllib.parse.quote(REDIRECT_URI, safe=' '))
    }
    res = requests.post(AUTHORIZATION_ENDPOINT, auth=HTTPBasicAuth(
        SERVICE_API_KEY, SERVICE_API_SECRET), data=authorization_payload)
    auth_response = res.json()
    pprint(auth_response)
    if auth_response['action'] not in ('INTERACTION', 'NO_INTERACTION'):
        print('Authorization request faield')
        sys.exit(1)

    print('Accessing authorization issue api...')
    issue_payload = {
        'ticket': auth_response['ticket'],
        'subject': "test user"
    }
    res = requests.post(AUTHORIZATION_ISSUE_ENDPOINT, auth=HTTPBasicAuth(
        SERVICE_API_KEY, SERVICE_API_SECRET), data=issue_payload)
    issue_response = res.json()
    if issue_response['action'] not in ('LOCATION', 'FORM'):
        print('Authorization issue request faield')
        sys.exit(1)

    pprint(issue_response)
    print('-------------------------------------------------------------')
    return issue_response['authorizationCode']


def token(code):
    print('Getting token...')
    token_payload = {
        'parameters': 'client_id={}&grant_type=authorization_code&code={}&redirect_uri={}'.format(CLIENT_ID, code, urllib.parse.quote(REDIRECT_URI, safe=' '))
    }
    res = requests.post(TOKEN_ENDPOINT, auth=HTTPBasicAuth(
        SERVICE_API_KEY, SERVICE_API_SECRET), data=token_payload)
    token_response = res.json()
    if token_response['action'] != 'OK':
        print('Token request failed')
        sys.exit(1)

    pprint(token_response)
    print('-------------------------------------------------------------')
    return (token_response['accessToken'], token_response['idToken'])


def user_info(access_token):
    print('Getting userInfo with access token...')
    user_info_payload = {
        'token': access_token
    }
    res = requests.post(USER_INFO_ENDPOINT, auth=HTTPBasicAuth(
        SERVICE_API_KEY, SERVICE_API_SECRET), data=user_info_payload)
    response = res.json()
    if response['action'] != 'OK':
        print('UserInfo request failed')
        sys.exit(1)

    pprint(response)
    print('-------------------------------------------------------------')
    return response['subject']


if __name__ == '__main__':
    authorization_code = authorization()
    access_token, id_token = token(authorization_code)
    user_info(access_token)
