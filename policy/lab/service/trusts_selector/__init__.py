#!/usr/bin/env python
import keystoneauth1.identity
from keystoneauth1 import loading
from keystoneauth1 import session
from keystoneclient import client as ks_client
from keystonemiddleware import auth_token
from oslo_config import cfg
from wsgiref import simple_server
import json
import logging
import os
import sys
from flask import Flask
from flask import request
from flask import render_template
from flask_bootstrap import Bootstrap


CONF = cfg.CONF
CONF(project='trusts_delegation')
loading.session.register_conf_options(cfg.CONF, 'communication')
vars = filter(lambda x: x[0].startswith('OS_'), os.environ.iteritems())
conf_keys = CONF.keys()
for k, v in vars:
# Try the full var first
    n = k.lower()
    cands = (n, n[3:])
    for var in cands:
        if var in conf_keys:
            self.conf.set_default(name=var, default=v)
            break

CONF(sys.argv[1:])
GROUP = 'service_auth'

loading.conf.register_conf_options(CONF, GROUP)
# MUST use 'auth_section'
try:
    auth = loading.conf.load_from_conf_options(CONF, GROUP)
except AttributeError, e:
    sys.exit('Configuration error: %s' % e)
except Exception, e:
    sys.exit('Unhandled exception: %s - %s' % (type(e), e.message))

# Initial session is for service user
SESSION = session.Session(auth=auth)

app = Flask(__name__)
Bootstrap(app)

def render_auth(auth):
    if isinstance(auth, keystoneauth1.identity.generic.password.Password):
        ret = {
            'project': auth._project_name,
            'username': auth._username,
        }
        return ret
    return None

def list_trusts(req):
    auth = req.environ['keystone.token_auth']
    ks = ks_client.Client('3', session=SESSION, auth=auth)
    user_id = ks.auth.client.get_user_id()
    user_type = ['trustor', 'trustee'] 

    def render_trust(trust):
        return trust._info

    ret = {}
    for t in user_type:
        key = 'as_' + t
        args = {}
        name = '%s_user' % t
        args[name] = user_id
        ret[key] = map(render_trust, ks.trusts.list(**args))
    return  {'trusts': ret}

@app.route('/')
def index():
    trusts = list_trusts(request)
    #return json.dumps(resp)
    return render_template('index.html', json=json, trusts=trusts)

@app.route('/token_info')
def render_token_info():
    kwargs = {
      'token_info': token_info(),
      'json': json
    }
    return render_template('token_info.html', **kwargs)

def token_info():
    return request.environ['keystone.token_info']

PORT = 5150
def main():
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(cfg.CONF.project)

    middleware = auth_token.AuthProtocol(app.wsgi_app, {})
    app.wsgi_app = middleware
    # See https://github.com/openstack/keystonemiddleware/blob/4.14.0/keystonemiddleware/auth_token/__init__.py#L663
    print('App credentials: %s' % render_auth(middleware._auth))
    middleware._conf.oslo_conf_obj.log_opt_values(logger, logging.DEBUG)
    # Just serve it simply
    server = simple_server.make_server('', PORT, app)
    server.serve_forever()
