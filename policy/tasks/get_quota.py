#!/usr/bin/env python
from cinderclient import client as cclient
from ks_auth import ks
from ks_auth import sess
from ks_auth import trust_auth
from ks_auth import utils
from novaclient import client as nclient
from pprint import pprint
from time import sleep
from utils import *
import cinderclient.exceptions
import sys


if __name__ == '__main__':
    version = 2
    nova = nclient.Client(version, session=sess)
    cinder = cclient.Client(version, session=sess)
    try:
        tenant_id = sys.argv[1]
    except IndexError:
        sys.exit('Supply a tenant id')

    def dump_accessinfo():
        for k, v in utils.access_info_vars(sess).iteritems():
            print('* {}: {}'.format(k, v))

    def test():
        args = {'tenant_id': tenant_id}
        info = {
            'novaclient': nova.quotas.get(**args).__dict__,
        }
        try:
            info['cinderclient'] = cinder.quotas.get(**args).__dict__
        except cinderclient.exceptions.Forbidden, e:
            print(e)

        pprint(info)

    print('Initial Auth Info:')
    for authtype, params in utils.initial_auth_info(ks.auth.client.session):
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
