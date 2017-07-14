#!/usr/bin/env python
# RDTIBCC-983
# Satisfies Requirements:

from cinderclient import client as cclient
from ks_auth import ks
from ks_auth import sess
from ks_auth import trust_auth
from ks_auth import utils
from novaclient import client
from novaclient import client as nclient
from pprint import pprint
from time import sleep
from utils import *
import cinderclient.exceptions
import novaclient.exceptions
import sys
VERSION = '2'
nova = client.Client(VERSION, session=sess)


def poll_volume(volume, interval=2, limit=4, *args, **kwargs):
    for i in range(0, limit):
        yield nova.volumes.get(volume.id)
        sleep(interval)


if __name__ == '__main__':
    def dump_accessinfo():
        for k, v in utils.access_info_vars(sess).iteritems():
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
        vols = {
            'cinderclient': cinder.volumes.list(),
            'novaclient': nova.volumes.list()
        }
        pprint(vols)
        print('Creating volume')
        print(' with: %s' % vol)
        vol_obj = None
        try:
            vol_obj = cinder.volumes.create(**vol)
            for state in poll_volume(vol_obj, interval=3, limit=5):
                if str(state.status).lower() == 'available' \
                    and hasattr(vol, 'os-vol-tenant-attr:tenant_id'):
                    break
            print(render_volume(vol_obj))
            print('Listing volumes')
            vols = {
                'cinderclient': cinder.volumes.list(),
                'novaclient': nova.volumes.list()
            }
            pprint(vols)
            print('Deleting volume')
            vol_obj.delete()
        except cinderclient.exceptions.OverLimit, e:
            print('Error: {}'.format(e))

        try:
            # wait for volume to leave 'deleting' state
            for state in poll_volume(vol_obj): pass
        except novaclient.exceptions.NotFound:
            print('* volume deleted')
        except Exception, e:
            print(e)

        print('Listing volumes')
        vols = {
            'cinderclient': cinder.volumes.list(),
            'novaclient': nova.volumes.list()
        }
        pprint(vols)

    print('Initial Auth Info:')
    for authtype, params in utils.initial_auth_info(ks.auth.client.session):
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
