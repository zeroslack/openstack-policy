#!/usr/bin/env python
from keystoneclient.v3 import client
from keystoneclient.auth.identity import v3
from keystoneclient.session import Session
from os import environ
import os
import cinderclient.client
import novaclient.client
try:
    import simplejson as json
except ImportError:
    import json

auth_args = {
    'endpoint': environ.get('SERVICE_ENDPOINT'),
    'token': environ.get('SERVICE_TOKEN'),
}

print(auth_args)
ks = client.Client(**auth_args)

# get the session
sess = ks.auth.client.session
nova = novaclient.client.Client(2, session=sess)
cinder = cinderclient.client.Client(2, session=sess)

print(cinder.volumes.list())
print(nova.volumes.list())
