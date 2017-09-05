#!/usr/bin/env python
from ka_auth import ks
from ka_auth import sess
from keystoneauth1.session import Session
from  keystoneauth1.exceptions.http import HTTPClientError
import os
import sys

if __name__ == '__main__':
    try:
        trustee_id = sys.argv[1]
    except IndexError:
        sys.exit('{} trustee_id [project_id]...'
                 ''.format(sys.argv[0].split('/')[-1]))

    endpoint_filter={
        'service_type': 'identity',
        'interface': 'public',
        'region_name': os.environ.get('OS_REGION')
    }
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
        try:
            res = ks.trusts.create(**args)
        except  HTTPClientError as e:
            # try direct session request
            if isinstance(sess, Session):
               req = {
                    u'trust': {
                        u'impersonation': impersonate,
                        u'project_id': args[u'project'],
                        u'roles': args[u'role_names'],
                        u'trustee_user_id': args[u'trustee_user'],
                        u'trustor_user_id': args[u'trustor_user'],
                    }
               }
               res = sess.post('/v3/OS-TRUST/trusts',
                         json=req,
                         endpoint_filter=endpoint_filter)

        print(res)
