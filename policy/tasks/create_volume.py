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
from novaclient import exceptions
from pprint import pprint
from time import sleep
from utils import *
from pbr.version import SemanticVersion
from pbr.version import VersionInfo
import sys

VERSION = '2'
nova = client.Client(VERSION, session=sess)


def poll_volume(volume, interval=2, limit=4, *args, **kwargs):
    for i in range(0, limit):
        yield nova.volumes.get(volume.id)
        sleep(interval)


if __name__ == '__main__':
    version = 2
    nova = nclient.Client(version, session=sess)
    cinder = cclient.Client(version, session=sess)

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

        MAX_SEMVER = SemanticVersion(major=3, minor=4, patch=0)
        semver = VersionInfo('python-novaclient').semantic_version()
        def list_nova_volumes():
            """Conditional on python-novaclient <= 3.3.0"""
            return nova.volumes.list() if semver <= MAX_SEMVER else []

        def get_nova_volume(volume_id):
            pass

        print('Listing volumes')
        vols = {
            'cinderclient': cinder.volumes.list(),
            'novaclient': list_nova_volumes(),
        }
        pprint(vols)

        print('Creating volume')
        print(' with: %s' % vol)
        # NB(kamidzi): os-vol-* attrs appear later
        vol = cinder.volumes.create(**vol)
        for state in poll_volume(vol):
            # wait for tenant_id attribute
            if str(state.status).lower() == 'available' \
                and hasattr(vol, 'os-vol-tenant-attr:tenant_id'):
                break
        pprint(render_volume(vol))
        print('Listing volumes')
        vols = {
            'cinderclient': cinder.volumes.list(),
            'novaclient': list_nova_volumes(),
        }
        pprint(vols)

    print('Initial Auth Info:')
    for authtype, params in utils.initial_auth_info(ks.auth.client.session):
        print(' %s' % authtype)
        print('  %s' % params)
    dump_accessinfo()

    print('Nova API: %s' % nova.api_version)
    test()

    # Test with trust credentials
    # switch to trust-based auth here
    # N.B. seems impersonation is broken?? - see accessinfo output
    try:
        print('Switching to trust-based auth')
        sess.auth = trust_auth
        dump_accessinfo()
        test()
    except Exception:
        sys.exit('No trust credentials')
