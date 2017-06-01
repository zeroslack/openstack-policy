#!/usr/bin/env python
from ks_auth import sess
from ks_auth import ks
from novaclient import client
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
print(target_servers)

for server in target_servers:
    server.stop()
    server.start()
