#!/usr/bin/env python
from ks_auth import ks
from pprint import pprint
import config
import itertools
import keystoneclient
import sys

if __name__ == '__main__':
    use_groups = getattr(config, 'use_groups', False)

    # add roles
    roles = []
    for role in config.role_names:
        try:
            roles += ks.roles.list(name=role)
            try:
                r = ks.roles.create(name=role)
                roles.append(r)
            except keystoneclient.exceptions.Conflict, e:
                # already there
                sys.stderr.write('ERROR - Create role "{}": {}\n'.format(role, e.message))
        except Exception, e:
            sys.stderr.write('ERROR - {}:{}\n'.format(e, e.message))

    # NB(kamidzi): Group-based approach will not work with LDAP identity backeend driver
    # add group
    if use_groups:
        try:
            name = config.service_group_name
            ks.groups.create(name=name,
                            description='Group for service users')

        except AttributeError, e:
            sys.stderr.write('ERROR - Configure "service_group_name": {}\n'.format(e.message))
        except keystoneclient.exceptions.Forbidden, e:
            sys.stderr.write('ERROR - Create group "{}": {}\n'.format(name, e.message))

    else:
        def get_project_id(name):
            try:
                proj = ks.projects.find(name=name)
                return proj.id
            except keystoneclient.exceptions.NotFound, e:
                sys.stderr.write('ERROR - Project "{}": {}\n'.format(name, e.message))

        def get_project(project_id):
            try:
                proj = ks.projects.get(project_id)
                return proj
            except keystoneclient.exceptions.NotFound, e:
                sys.stderr.write('ERROR - Project "{}": {}\n'.format(proj_id, e.message))

        project_ids = config.project_ids if hasattr(config, 'project_ids') else []
        project_ids += map(get_project_id, config.project_names)
        projects = map(get_project, project_ids)

        def lookup_user(username):
            try:
                users = ks.users.list(name=username)
                return users
            except keystoneclient.exceptions.NotFound, e:
                sys.stderr.write('ERROR - User "{}": {}\n'.format(username, e.message))

        # Get the user objects
        users = list(itertools.chain.from_iterable(map(lookup_user,
                                                  config.user_names)))
        # assign roles
        for role in roles:
            for project in projects:
                for user in users:
                    kwargs = {
                        'role': role,
                        'user': user,
                        'project': project,
                    }
                    ks.roles.grant(**kwargs)

            # Dump the role assignments
            pprint(role)
            pprint(ks.role_assignments.list(role=role))
