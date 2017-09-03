#!/usr/bin/env python 
try:
    import simplejson as json
except ImportError:
    import json
import requests

url = 'https://openstack.bcpc.example.com:5000/v3/auth/tokens'
auth_params = {
  u'auth': {
    u'identity': {
      u'methods': [u'password'],
      u'password': {
        u'user': {
          u'domain': {u'name': u'default'},
          u'name': u'admin',
          u'password': u'5T16_T0IEBaNEn7B2rZ6'
        }
      }
    },
  }
}
#    u'scope': {
#      u'project': {
#        u'domain': {u'name': u'Default'},
#        u'name': u'service'
#      }
#    }
#  }
#}

kwargs = {
    'allow_redirects': False,
    'headers': {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'User-Agent': 'privs_escalation.py keystoneauth1/2.21.0 python-requests/2.18.1 CPython/2.7.6'
    },
    'verify': True
}

kwargs['data'] = json.dumps(auth_params)
resp = requests.post(url, **kwargs)
from pprint import pprint
pprint(resp.headers)
pprint(resp.json())

