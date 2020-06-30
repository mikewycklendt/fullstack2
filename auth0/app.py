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
    jwks = json.loads(jsonurl.read().decode('utf-8'))
    print(jwks)
    rsa_key = {}
    #if 'kid' not in unverified_header:
    #    raise AuthError({
    #        'code': 'invalid_header',
    #        'description': 'Authorization malformed.'
    #    }, 401)

    for key in jwks['keys']:
        #if key['kid'] == unverified_header['kid']:
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
                algorithms=['RS256'],
                audience='image',
                issuer='https://dcadventuresonline.us.auth0.com/',
                verify="""-----BEGIN CERTIFICATE-----
MIIDGTCCAgGgAwIBAgIJBX4hAZSVEupoMA0GCSqGSIb3DQEBCwUAMCoxKDAmBgNV
BAMTH2RjYWR2ZW50dXJlc29ubGluZS51cy5hdXRoMC5jb20wHhcNMjAwNjIyMTYy
MTAzWhcNMzQwMzAxMTYyMTAzWjAqMSgwJgYDVQQDEx9kY2FkdmVudHVyZXNvbmxp
bmUudXMuYXV0aDAuY29tMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA
s3OYchfjFBg3CE2RGCUyToRFr0MpSvEvdGVFwOd+C2Lme1wDXo5lHOHH47e7ONgj
jTvIZja/1L+Fk/CeemC3VRvX/turVFIURlk0MbU315nS1yMPz3CB7FONisjrntjE
+HrSj80HqWhvgIQyNFQoWbBc+2hU1j8oM4MtwPNSiYkCE4Q8Uk1RURSiF8jiKPP1
61hJ0GUU2LraoQHEmF9Z7euDyKPUwpszx/YNsE3cInZDx7ABreTqM71ZHAATFPio
z+oVKIp8f2MYJLLfY/2Os6dCqeevRX7ay0GCPpC7kwQUAO1ceA13u6Vl5dljushY
xBh4kbFkuWwLNSqhpVl7KwIDAQABo0IwQDAPBgNVHRMBAf8EBTADAQH/MB0GA1Ud
DgQWBBThbAc56UTKY+opdCI0oDEU+h39ZjAOBgNVHQ8BAf8EBAMCAoQwDQYJKoZI
hvcNAQELBQADggEBAHHu9jWAexNHeSK2NBx85gv+EIynUAYaUE04UYzg9aEpUENC
RRKem0EsoeVXwpICX8WPQ5rCZdSjusy2c8AD3wGfF/taY3pHrLPp16EYFjlydu5n
r9Rvi5KN2B/BBjmcYVE78s83xgr2ngGstiEmeszxsHyIvz06+0IrCAUzq7Fi0kRw
qWRzGrUU3Y9TYKRmoq6pTD1UXP7RtihK4BL3I0DhYYv/fHITtwemuXz/TYtE/s6a
exyuu7z4xUjhWiqQvJTw2K1ItlB1UK3CFD1fbzCxEUFLA5ourJlaJQ1I/1rXjUWT
6HtbxNyx3TvV6+u5s1ZM/y8hN+xpLfFA+QAWcss=
-----END CERTIFICATE-----"""
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