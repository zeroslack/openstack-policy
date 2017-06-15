#!/usr/bin/env python
# RDTIBCC-983
# Satisfies Requirements:
from cinderclient import client as cclient
from ks_auth import ks
from ks_auth import sess
from ks_auth import trust_auth
from novaclient import client
from novaclient import client as nclient
from novaclient import exceptions
from pprint import pprint
from time import sleep
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


def poll_volume(volume, interval=2, limit=4, *args, **kwargs):
    for i in range(0, limit):
        yield nova.volumes.get(volume.id)
        sleep(interval)


if __name__ == '__main__':

    def render_volume(vol):
        attrs = [
            'size',
            'name',
            'description',
            'volume_type',
            'user_id',
            'project_id',
            'metadata',
            'imageRef',
            'by',
            'instance',
        ]
        return dict(filter(lambda x: x[0] in attrs, vol.__dict__.iteritems()))

    def dump_accessinfo():
        for k, v in access_info_vars(sess).iteritems():
            print('* {}: {}'.format(k, v))

    def test():
        extras = {}
        for i, k in enumerate(['project_id', 'user_id'], 1):
            try:
                extras[k] = sys.argv[i]
            except IndexError:
                pass
        vol = {
            'name': 'test-volume',
            'size': 1
        }
        vol.update(extras)
        print('Listing volumes')
        print('* using cinderclient:')
        cinder.volumes.list()
        print('* using novaclient:')
        nova.volumes.list()

        print('Creating volume')
        print(' with: %s' % vol)
        vol = cinder.volumes.create(**vol)
        for state in poll_volume(vol):
            if str(state.status).lower() == 'active':
                break
        print(render_volume(vol))
        print('Listing volumes')
        print('* using cinderclient:')
        cinder.volumes.list()
        print('* using novaclient:')
        nova.volumes.list()
        print('Deleting volume')
        vol.delete()
        print('* using cinderclient:')
        cinder.volumes.list()
        print('* using novaclient:')
        nova.volumes.list()    # Print some info

    print('Initial Auth Info:')
    for authtype, params in initial_auth_info(ks.auth.client.session):
        print(' %s' % authtype)
        print('  %s' % params)
    dump_accessinfo()

    version = 2
    nova = nclient.Client(version, session=sess)
    cinder = cclient.Client(version, session=sess)
    print('Nova API: %s' % nova.api_version)
    test()

    # switch to trust-based auth here
    print('Switching to trust-based auth')
    sess.auth = trust_auth
    dump_accessinfo()
    # N.B. - will create volume with user_id set to _trustee_id_
    # (with impersonation off), but still only visible by trustor as expected
    test()
