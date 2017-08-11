#!/usr/bin/env python
from ks_auth import ks
import sys

if __name__ == '__main__':
    try:
        trustee_id = sys.argv[1]
    except IndexError:
        sys.exit('{} trustee_id [project_id]...'
                 ''.format(sys.argv[0].split('/')[-1]))

    projects = sys.argv[2:]
    if not len(projects):
        sys.stderr.write('No projects specified. Creating trust on all.\n')
        projects = ks.auth.projects()
        names = map(lambda x: x.name, projects)
        print('Available projects: %s' % names)

    # Make sure to match authenticated user
    trustor = ks.auth.client.get_user_id()
    impersonate = False

    for project in projects:
        project_id = project.id if hasattr(project, 'id') else project
        args = {
            'trustee_user': trustee_id,
            'trustor_user': trustor,
            'role_names': ['Member'],
            'project': project_id,
            'impersonation': impersonate,
        }
        res = ks.trusts.create(**args)
        print(res)
