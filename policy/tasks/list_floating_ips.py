#!/usr/bin/env python
from ks_auth import sess
from novaclient import client

version = 2
nova = client.Client(version, session=sess)
print('Nova API: %s' % nova.api_version)
ip_list = nova.floating_ips.list()
print(ip_list)
