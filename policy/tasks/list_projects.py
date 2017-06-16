#!/usr/bin/env python
from ks_auth import ks
from pprint import pprint
# RDTIBCC-983
# Satisfies Requirements:
#  - list a users Tenancies/projects
#  - list tenants/projects

# all
# identity:list_projects
print('* All Projects *')
pprint(ks.projects.list())

# identity:list_users
users = ks.users.list()
for u in users:
    print('* Projects for %s:' % u.name)
    # identity:list_user_projects
    pprint(ks.projects.list(user=u))
