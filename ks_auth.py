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

# Add trust auth if possible
try:
    trust_auth_args = dict(auth_args)
    trust_id = environ['OS_TRUST_ID']
    trust_auth_args['trust_id'] = trust_id
    #conflicts = ['project_domain_name', 'project_name', 'user_domain_name']
    conflicts = ['project_name']
    for var in conflicts:
        del trust_auth_args[var]
    trust_auth = plugin(**trust_auth_args)
except KeyError:
    trust_auth = None

auth = plugin(**auth_args)
sess = Session(auth=auth)
ks = client.Client(session=sess)
