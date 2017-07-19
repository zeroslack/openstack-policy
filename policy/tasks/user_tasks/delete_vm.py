#!/usr/bin/env python
from ks_auth import sess
from ks_auth import trust_auth
from ks_auth import ks
from ks_auth import utils
from novaclient import client
import novaclient.exceptions
from time import sleep
from uuid import uuid4
import sys

# RDTIBCC-1042

VERSION = '2'
nova = client.Client(VERSION, session=sess)

username = 'standard_user'
search_opts = {
    'all_tenants': True
}

class PollingLimitException(Exception):
    pass

def poll_server(server, interval=2, limit=4, *args, **kwargs):
    for i in range(0, limit):
        yield nova.servers.get(server.id)
        sleep(interval)
    raise PollingLimitException()

def is_active(server):
    return (server.status == 'ACTIVE')

def is_shutoff(server):
    return (server.status == 'SHUTOFF')


if __name__ == '__main__':
    try:
        instance_id = sys.argv[1]
    except IndexError:
        sys.exit('Specify an instance_id')

    # Print some info
    print('Initial Auth Info:')
    for authtype, params in utils.initial_auth_info(ks.auth.client.session):
        print(' %s' % authtype)
        print('  %s' % params)

    print('Access Info:')
    for k, v in utils.access_info_vars(sess).iteritems():
        print('* {}: {}'.format(k, v))

    retry_count = 3
    try:
        server = nova.servers.get(instance_id)
        print('* Deleting %s' % server.name)
        for i in range(1, retry_count+1):
            print('** Attempt %d' % i)
            server.delete()
            try:
                for state in poll_server(server):
                    if state == 'DELETING':
                        print('** still deleting')
            except novaclient.exceptions.NotFound:
                print('*** done deleting')
                break
    except Exception, e:
        print(e)
