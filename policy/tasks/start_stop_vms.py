#!/usr/bin/env python
from ks_auth import ks
from ks_auth import sess
from ks_auth import trust_auth
from ks_auth import utils
from novaclient import client
from novaclient import exceptions
from time import sleep
import sys
# RDTIBCC-983
# Satisfies Requirements:
#  - start a vm
#  - stop a vm

# depends upon 'provisioner' role
VERSION = '2'
DEFAULT_USERNAME = 'standard_user'

try:
    username = sys.argv[1]
except IndexError:
    sys.stderr.write('No username specified. Using {}\n'
                     ''.format(DEFAULT_USERNAME))
    username = DEFAULT_USERNAME

search_opts = {
    'all_tenants': True
}

nova = client.Client(VERSION, session=sess)

def poll_server(server, interval=2, limit=4, *args, **kwargs):
    for i in range(0, limit):
        yield nova.servers.get(server.id)
        sleep(interval)


def is_shutoff(server):
    return (server.status == 'SHUTOFF')

# Print some info
print('Initial Auth Info:')
for authtype, params in utils.initial_auth_info(ks.auth.client.session):
    print(' %s' % authtype)
    print('  %s' % params)

print('Access Info:')
for k, v in utils.access_info_vars(sess).iteritems():
    print('* {}: {}'.format(k, v))

# list all servers
# BUG(kmidzi): all_tenants=True appears busted
# As of https://github.com/bloomberg/chef-bcpc/blob/6.4.0/cookbooks/bcpc/attributes/nova.policy.rb
print('** All servers **')
print(nova.servers.list(search_opts=search_opts))

users = ks.users.list(name=username)
try:
    user = users[0]
    search_opts['user_id'] = user.id
    print('** Servers for %s: ' % user.name)
    user_servers = nova.servers.list(search_opts=search_opts)
    print(user_servers)

    target_servers = filter(lambda x: x.user_id == user.id, user_servers)
    print('Targeting:')
    print(target_servers)

    # switch to trust-based auth here
    # N.B. seems impersonation is broken?? - see accessinfo output
    print('Switching to trust-based auth')
    sess.auth = trust_auth
    # print access info again
    print('Access Info:')
    for k, v in utils.access_info_vars(sess).iteritems():
        print('* {}: {}'.format(k, v))

    retry_count = 3
    for server in target_servers:
        stopped = False
        try:
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
        except exceptions.Conflict, e:
            target_msg = r' it is in vm_state stopped'
            if e.message.find(target_msg) != -1:
                print('*** skipping stop action - already stopped.')
            else:
                raise
        # Below happens when trust not scoped to project of server
        except exceptions.NotFound, e:
            print('** ERROR: {} - {}'.format(server.name, e.message))
            continue

        print('* Starting %s' % server.name)
        server.start()
except Exception, e:
    sys.exit(e.message)
