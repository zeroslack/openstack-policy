#!/usr/bin/env python
import requests
from os import environ
import os
try:
    import simplejson as json
except ImportError:
    import json

auth_args = {
    'user_domain_name': environ.get('OS_USER_DOMAIN_NAME'),
    'project_domain_name': environ.get('OS_PROJECT_DOMAIN_NAME'),
    'auth_url': environ.get('OS_AUTH_URL'),
    'password': environ.get('OS_PASSWORD'),
    'username': environ.get('OS_USERNAME'),
    'trust_id': environ.get('OS_TRUST_ID')
}

params = {
    "auth": {
        "identity": {
            "methods": [
                "password"
            ],
            "password": {
                "user": {
                    "domain": {
                        "name": auth_args['user_domain_name'],
                    },
                    "name": auth_args['username'],
                    "password": auth_args['password'],
                }
            }
        },
        "scope": {
            "OS-TRUST:trust": {
                "id": auth_args['trust_id']
            }
        }
    }
}
req = json.dumps(params)

url = auth_args['auth_url'] + '/auth/tokens'
r = requests.post(url, data=req)
print(json.dumps(dict(r.headers), indent=2))
print(json.dumps(r.json(), indent=2))
