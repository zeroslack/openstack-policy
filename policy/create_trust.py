#!/usr/bin/env python
from ks_auth import ks
import sys

if __name__ == '__main__':
    try:
        trustee_id = sys.argv[1]
    except IndexError:
        sys.exit('Supply a trustee id')

    projects = ks.auth.projects()
    names = map(lambda x: x.name, projects)
    print('Available projects: %s' % names)

    # Make sure to match authenticated user
    trustor = ks.auth.client.get_user_id()
    impersonate = False

    for project in projects:
        project_id = project.id
        args = {
            'trustee_user': trustee_id,
            'trustor_user': trustor,
            'role_names': ['Member'],
            'project': project_id,
            'impersonation': impersonate,
        }
        res = ks.trusts.create(**args)
        print(res)
