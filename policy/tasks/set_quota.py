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
import novaclient.exceptions
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
        FORBIDDEN_EXCEPTIONS = (novaclient.exceptions.Forbidden,cinderclient.exceptions.Forbidden)
        CLIENT_EXCEPTIONS = (novaclient.exceptions.ClientException,cinderclient.exceptions.ClientException)
        _clients = {
            'novaclient': nova,
            'cinderclient': cinder,
        }
        def _get_info():
            def _filter_keys(hash):
                keys = ['id', '_info', '_loaded', 'manager']
                l = list(hash.iteritems())
                return dict(filter(lambda x: x[0] not in keys, l))

            args = {'tenant_id': tenant_id}
            # Get results for each client

            results = {}
            for key, client in _clients.iteritems():
                try:
                    rendered = render_managed_obj(client.quotas.get(**args))
                    results[key] = _filter_keys(rendered)
                except FORBIDDEN_EXCEPTIONS, e:
                    results[key] = None
                    print('Error [{}]: {}'.format(key, e))
            return results

        print('Initial Quotas')
        info = _get_info()
        pprint(info)
        quota_args = {
            'novaclient': {
                'fixed_ips': 0,
                'injected_file_content_bytes': 0,
                'injected_file_path_bytes': 0,
                'injected_files': 0,
                'key_pairs': 0,
                'metadata_items': 0,
                'security_group_rules': 0,
                'security_groups': 5,
                'server_group_members': 0,
                'server_groups': 0,
            },
            'cinderclient':{
                'backups': 0,
                'gigabytes': 0,
            }
        }

        # Map the original values
        restore_args = {}
        res = []
        for key, client in _clients.iteritems():
            restore_args[key] = dict(info[key] or {})
            print('* Setting {} quotas *'.format(key))
            try:
                res = client.quotas.update(tenant_id, **quota_args[key])
                pprint(res)
            except FORBIDDEN_EXCEPTIONS + CLIENT_EXCEPTIONS, e:
                print('Error [{}]: {}'.format(key, e))

            try:
            # Restore original quota
                client.quotas.update(tenant_id, **restore_args[key])
            except FORBIDDEN_EXCEPTIONS + CLIENT_EXCEPTIONS, e:
                print('Error [{}]: {}'.format(key, e))
            except Exception, e:
                print e.__class__


    print('Initial Auth Info:')
    for authtype, params in utils.initial_auth_info(ks.auth.client.session):
        print(' %s' % authtype)
        print('  %s' % params)
    dump_accessinfo()

    print('Nova API: %s' % nova.api_version)
    print('Cinder API: %s' % cinder.get_volume_api_version_from_endpoint())
    test()

    # switch to trust-based auth here
    print('Switching to trust-based auth')
    try:
        sess.auth = trust_auth
        dump_accessinfo()
        test()
    except Exception, e:
        # TODO(kamidzi): too general
        sys.exit('No trust credentials')

# vim:ts=4:sw=4:et:smartindent:shiftround
