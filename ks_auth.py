#!/usr/bin/env python
from keystoneclient.v3 import client
from keystoneclient.auth.identity import v3
from keystoneclient.session import Session
from os import environ
import os
try:
    import simplejson as json
except ImportError:
    import json

username = environ.get('OS_USERNAME')
auth_args = {
        'user_domain_name': environ.get('OS_USER_DOMAIN_NAME'),
        'project_domain_name': environ.get('OS_PROJECT_DOMAIN_NAME'),
        'project_name': environ.get('OS_PROJECT_NAME',environ.get('OS_TENANT_NAME')),
        'auth_url': environ.get('OS_AUTH_URL'),
        'password': environ.get('OS_PASSWORD'),
        'username': username,
}

plugin = v3.Password
auth = plugin(**auth_args)
sess = Session(auth=auth)
ks = client.Client(session=sess)
