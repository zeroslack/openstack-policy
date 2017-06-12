#!/usr/bin/env python
from ks_auth import sess
from ks_auth import trust_auth
from ks_auth import ks
from novaclient import client
from novaclient import exceptions
from time import sleep
# RDTIBCC-983
# Satisfies Requirements:
#  - start a vm
#  - stop a vm

# depends upon 'provisioner' role
VERSION = '2'
nova = client.Client(VERSION, session=sess)

username = 'standard_user'
search_opts = {
    'all_tenants': True
}


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


#s.auth.auth_methods[0].get_auth_data(s,s.auth,{})
#('password', {'user': {'domain': {'name': 'default'}, 'password': 'VZ3fVYlsjDqpTkwCY8M6', 'name': 'admin'}})
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


def poll_server(server, interval=2, limit=4, *args, **kwargs):
    for i in range(0, limit):
        yield nova.servers.get(server.id)
        sleep(interval)


def is_active(server):
    return (server.status == 'ACTIVE')

# Print some info
print('Initial Auth Info:')
for authtype, params in initial_auth_info(ks.auth.client.session):
    print(' %s' % authtype)
    print('  %s' % params)

print('Access Info:')
for k, v in access_info_vars(sess).iteritems():
    print('* {}: {}'.format(k, v))

# list all servers
# BUG(kmidzi): all_tenants=True appears busted
# As of https://github.com/bloomberg/chef-bcpc/blob/6.4.0/cookbooks/bcpc/attributes/nova.policy.rb
print('** All servers **')
print(nova.servers.list(search_opts=search_opts))

users = ks.users.list(name=username)
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
for k, v in access_info_vars(sess).iteritems():
    print('* {}: {}'.format(k, v))

retry_count = 3
for server in target_servers:
    try:
        print('* Stopping %s' % server.name)
        for i in range(1, retry_count+1):
            print('** Attempt %d' % i)
            server.stop()
            for state in poll_server(server):
                # TODO(kamidzi): still maybe race condition with SHUTOFF state.
                # print state.status
                if is_active(state):
                    print '*** shutting down...'
    except exceptions.Conflict, e:
        target_msg = r' it is in vm_state stopped'
        if e.message.find(target_msg) != -1:
            print('*** skipping stop action - already stopped.')
        else:
            raise
    print('* Starting %s' % server.name)
    server.start()
