from flask import Flask, request, abort, url_for
import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from splinter import browser
import requests
import os
import http.client

app = Flask(__name__)

AUTH0_DOMAIN = 'dcadventuresonline.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'image'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header"""
    
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    
    return token


def verify_decode_jwt(token):
    print(token)
    jsonurl = urlopen('https://dcadventuresonline.us.auth0.com/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    print(jwks)
    unverified_header = token
    rsa_key = {}
    #if 'kid' not in unverified_header:
    #    raise AuthError({
    #        'code': 'invalid_header',
    #        'description': 'Authorization malformed.'
    #    }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)


def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_token_auth_header()
        try:
            payload = verify_decode_jwt(token)
        except:
            abort(401)
        return f(payload, *args, **kwargs)

    return wrapper

@app.route('/headers')
@requires_auth
def headers(payload):
    print(payload)
    return 'Access Granted'

@app.route('/callback')
def callback():
    #token_url = request.Rawurl
    #token_split = token_url.split('#')
    #token = token_split[1]
    #print(token_url)
    #return token_url
    payload = {'grant_type':'client_credentials',
                'client_id':'JXHzBwF6DPiXU2fBjPe1Nd7bYPC6vZ0o',
                'client_secret':'aSEqerZw31L19r9QzdcbrLBIVY3i2WD3U6Cd2kBwY0MIKWJrlMNny6A7nySzlSS1',
                'audience':'image'
                }
    request_headers = { 'content-type': "application/x-www-form-urlencoded" }

    url = "https://dcadventuresonline.us.auth0.com/oauth/token"

    response = requests.post(url=url, headers=request_headers, data=payload)
    print(response.json())
    data = response.json()
    token = data['access_token']
    verify_decode_jwt(token)
    #access_token = {'access_token': payload.decode('RS256')}
    #print(access_token)
    print(payload)
    return payload

@app.route('/login')
def get_token():
    #conn = http.client.HTTPSConnection("")

    payload = {'grant_type':'client_credentials',
                'client_id':'JXHzBwF6DPiXU2fBjPe1Nd7bYPC6vZ0o',
                'client_secret':'aSEqerZw31L19r9QzdcbrLBIVY3i2WD3U6Cd2kBwY0MIKWJrlMNny6A7nySzlSS1',
                'audience':'image'
                }
    request_headers = { 'content-type': "application/x-www-form-urlencoded" }

    url = "https://dcadventuresonline.us.auth0.com/oauth/token"

    response = requests.post(url=url, headers=request_headers, data=payload)
    print(response.json())
    data = response.json()
    token = data['access_token']
    decoded_token = jwt.decode(token)
    print(decoded_token)
    return decoded_token
    #verify_decode_jwt(token)
    #access_token = {'access_token': payload.decode('RS256')}
    #print(access_token)
    

    #print(data)
    #return(data)


    #conn.request("POST", "https://dcadventuresonline.us.auth0.com/oauth/token", payload, request_headers)

    #res = conn.getresponse()
    #data = res.read()


    #print(data)
    #return data


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=80)

"""
https://dcadventuresonline.us.auth0.com/authorize?audience=image&response_type=token&client_id=JXHzBwF6DPiXU2fBjPe1Nd7bYPC6vZ0o&redirect_uri=https://dcadventuresonline.com/callback
"""
"""
https://dcadventuresonline.us.auth0.com/oauth/token?audience=image&grant_type=client_credentials&client_id=JXHzBwF6DPiXU2fBjPe1Nd7bYPC6vZ0o&client_secret=aSEqerZw31L19r9QzdcbrLBIVY3i2WD3U6Cd2kBwY0MIKWJrlMNny6A7nySzlSS1
"""