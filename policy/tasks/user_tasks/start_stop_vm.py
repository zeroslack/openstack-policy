#!/usr/bin/env python
from ks_auth import sess
from ks_auth import trust_auth
from ks_auth import ks
from ks_auth import utils
from novaclient import client
import novaclient.exceptions
from time import sleep
import sys
# RDTIBCC-1042

VERSION = '2'
nova = client.Client(VERSION, session=sess)

username = 'standard_user'
search_opts = {
    'all_tenants': True
}

def poll_server(server, interval=2, limit=4, *args, **kwargs):
    for i in range(0, limit):
        yield nova.servers.get(server.id)
        sleep(interval)

def is_shutoff(server):
    return (server.status == 'SHUTOFF')


if __name__ == '__main__':
    try:
        instance_id = sys.argv[1]
        target_ids = sys.argv[1:]
    except IndexError:
        sys.exit('Supply instance_id [instance_id]...')

    # Print some info
    print('Initial Auth Info:')
    for authtype, params in utils.initial_auth_info(ks.auth.client.session):
        print(' %s' % authtype)
        print('  %s' % params)

    print('Access Info:')
    for k, v in utils.access_info_vars(sess).iteritems():
        print('* {}: {}'.format(k, v))

    retry_count = 3
    for instance_id in target_ids:
        stopped = False
        try:
            server = nova.servers.get(instance_id)
            print('* Stopping %s' % server.name)
            for i in range(1, retry_count+1):
                if stopped:
                    break
                print('** Attempt %d' % i)
                server.stop()
                for state in poll_server(server):
                    # TODO(kamidzi): still maybe race condition with SHUTOFF state.
                    if is_shutoff(state):
                        stopped = True
                        break
                    print '*** shutting down...'
        except novaclient.exceptions.NotFound, e:
            print(e)
            continue
        except exceptions.Conflict, e:
            target_msg = r' it is in vm_state stopped'
            if e.message.find(target_msg) != -1:
                print('*** skipping stop action - already stopped.')
            else:
                raise
        print('* Starting %s' % server.name)
        server.start()
