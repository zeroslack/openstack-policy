#!/usr/bin/env python
from keystoneauth1 import loading
from keystoneclient import client
from keystoneauth1.exceptions.http import NotFound
from keystoneauth1.session import Session
import os
from pprint import pprint
try:
    import simplejson as json
except ImportError:
    import json

tauth_args = {
    'endpoint': os.environ.get('OS_URL'),
    'token': os.environ.get('OS_TOKEN')
}

username = os.environ.get('OS_USERNAME')
pauth_args = {
        'user_domain_name': os.environ.get('OS_USER_DOMAIN_NAME'),
        'project_domain_name': os.environ.get('OS_PROJECT_DOMAIN_NAME'),
        'project_name': os.environ.get('OS_PROJECT_NAME'),
        'auth_url': os.environ.get('OS_AUTH_URL'),
        'password': os.environ.get('OS_PASSWORD'),
        'username': username,
}

if __name__ == '__main__':
    auth_args = pauth_args
    plugin = 'v3password'
    region = os.environ.get('OS_REGION_NAME')
    endpoint_filter = {
        'service_type': 'identity',
        'interface': 'admin',
        'region_name': region
    }

    loader = loading.get_plugin_loader(plugin)
    auth = loader.load_from_options(**auth_args)
    sess = Session(auth=auth)
    ks = client.Client(session=sess)
    # Available projects
    print('Available projects:')
    pprint(ks.auth.projects())
    print('Available domains:')
    domains = ks.auth.domains()
    if domains:
        pprint(domains)
    else:
        resp = sess.get('/auth/domains', endpoint_filter=endpoint_filter)
        print(json.dumps(resp.json(), indent=2))

    token = sess.get_token()
    token_data = ks.tokens.get_token_data(token=token, include_catalog=False)
    print('Token data:')
    print(json.dumps(token_data, indent=2))

    dname = 'dev'
    try:
        domain = ks.domains.get(dname)
        domain_id = None
    except NotFound:
        # Direct API
        resp = sess.get('/domains?name={}'.format(dname),
                        endpoint_filter=endpoint_filter)
        domain = resp.json()
        # For some strange reason, this is array
        domain_id = filter(lambda x: x['name'] == dname,
                           domain['domains'])[0]['id']
    print('Domain - %s:' % dname)
    print(json.dumps(domain, indent=2))
    print("* ks.users.list(name='{uname}'"
          ",domain='{domain}')):".format(uname=username, domain=dname))
    print(ks.users.list(name=username, domain=dname))
    resp = sess.get('/users?domain_id={id}'
                    '&name={name}'.format(name=username, id=domain_id),
                    endpoint_filter=endpoint_filter)
    user = resp.json()
    print('User: ')
    print(json.dumps(user, indent=2))
