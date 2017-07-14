#!/usr/bin/env python
from ks_auth import ks
from ks_auth import sess
from ks_auth import trust_auth
from ks_auth import utils
from novaclient import client
from novaclient import exceptions
from pprint import pprint
from time import sleep
import sys
# RDTIBCC-983
# Satisfies Requirements:
#  - attach a float
#  - detach a float

# depends upon 'provisioner' role
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


def get_float_ip():
    """Attempts to acquire floating ip by first looking for existing
    unallocated, then creating."""
    curr_list = nova.floating_ips.list()
    print(curr_list)
    def unallocated(ip):
        return (ip.instance_id == None == ip.fixed_ip )
    try:
        cands = filter(unallocated, curr_list)
        return cands.pop()
    except IndexError:
        # allocate one
        pools = nova.floating_ip_pools.list()
        for pool in pools:
            try:
                ip = nova.floating_ips.create(pool=pool.name)
                return ip
            except Exception, e:
                print(e)

if __name__ == '__main__':
    try:
        instance_id = sys.argv[1]
    except IndexError:
        sys.exit('Supply an instance id')

    def test():
        """Run the actual test.
        - Acquire (retrieve/allocate) float
        - attach
        - detach
        """
        ip = get_float_ip()
        server = nova.servers.get(instance_id)
        print('Using ip: %s' % ip)

        actions = ['add', 'remove']
        for action in actions:
            meth = getattr(server, '%s_floating_ip' % action)
            print('* Calling %s' % meth.__name__)
            meth(address=ip)
            s = nova.servers.get(instance_id)
            pprint(s.addresses)

    # Print some info
    print('Initial Auth Info:')
    for authtype, params in utils.initial_auth_info(ks.auth.client.session):
        print(' %s' % authtype)
        print('  %s' % params)

    print('Access Info:')
    for k, v in utils.access_info_vars(sess).iteritems():
        print('* {}: {}'.format(k, v))

    # Test with service credentials
    try:
        test()
    except exceptions.ClientException, e:
        print('!! Using service credentials failed somewhere: %s' % e.message)

    # Test with trust credentials
    # switch to trust-based auth here
    # N.B. seems impersonation is broken?? - see accessinfo output
    print('Switching to trust-based auth')
    sess.auth = trust_auth
    # print access info again
    print('Access Info:')
    for k, v in utils.access_info_vars(sess).iteritems():
        print('* {}: {}'.format(k, v))

    test()
