#!/usr/bin/env python
from cinderclient import client as cclient
from ks_auth import ks
from ks_auth import sess
from ks_auth import trust_auth
from novaclient import client
from novaclient import client as nclient
from novaclient import exceptions
from pprint import pprint
from time import sleep
from utils import *
import sys

VERSION = '2'
nova = client.Client(VERSION, session=sess)


def access_info_vars(session):
    """Expects keystoneclient.session.Session"""
    to_return = [
        'trust_id',
        'trust_scoped',
        'trustee_user_id',
        'trustor_user_id',
        'user_domain_name',
        'username',
    ]
    ai = ks.auth.client.session.auth.get_access(sess)
    ret = map(lambda k: (k, getattr(ai, k)), to_return)
    return dict(ret)


def initial_auth_info(session, auth_filter=lambda x: x[0] == 'password'):
    ret = []
    auth = session.auth
    auth_data = map(lambda x: x.get_auth_data(session, auth, {}),
                    auth.auth_methods)
    filtered = filter(auth_filter, auth_data)
    for authtype, params in filtered:
        try:
            params['user']['password'] = '****'
        except KeyError:
            pass
        ret.append((authtype, params))
    return ret


if __name__ == '__main__':
    version = 2
    nova = nclient.Client(version, session=sess)
    cinder = cclient.Client(version, session=sess)
    try:
        volume_id = sys.argv[1]
    except IndexError:
        sys.exit('Supply a volume id')

    def dump_accessinfo():
        for k, v in access_info_vars(sess).iteritems():
            print('* {}: {}'.format(k, v))

    def test():
        args = {'volume_id': volume_id}
        info = {
            'novaclient': nova.volumes.get(**args).__dict__,
            'cinderclient': cinder.volumes.get(**args).__dict__,
        }
        pprint(info)

    print('Initial Auth Info:')
    for authtype, params in initial_auth_info(ks.auth.client.session):
        print(' %s' % authtype)
        print('  %s' % params)
    dump_accessinfo()

    print('Nova API: %s' % nova.api_version)
    test()

    # switch to trust-based auth here
    print('Switching to trust-based auth')
    try:
        sess.auth = trust_auth
        dump_accessinfo()
        test()
    except:
        # TODO(kamidzi): too general
        sys.exit('No trust credentials')
