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

try:
    trust_id = environ['OS_TRUST_ID']
    auth_args['trust_id'] = trust_id
    #conflicts = ['project_domain_name', 'project_name', 'user_domain_name']
    conflicts = ['project_name']
    for var in conflicts:
        del auth_args[var]
except KeyError:
    pass

plugin = v3.Password
auth = plugin(**auth_args)
sess = Session(auth=auth)
ks = client.Client(session=sess)
