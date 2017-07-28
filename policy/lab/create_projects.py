#!/usr/bin/env python
from ks_auth import ks
from pprint import pprint
import sys
import keystoneclient
try:
    import config
except ImportError:
    sys.exit('Place a config.py in project directory.')

domain = 'Default'
if __name__ == '__main__':
    # add projects
    projects = []
    for name in config.project_names:
        try:
            p = ks.projects.create(name=name, domain=domain)
            projects.append(p)
        except keystoneclient.exceptions.Conflict, e:
            sys.stderr.write('WARNING - "{}": {}\n'.format(name, e.message))
            try:
                plist = ks.projects.list(name=name)
                projects.extend(plist)
                # already there
            except:
                sys.stderr.write('ERROR - {}:{}\n'.format(e, e.message))
                # some error?
                sys.exit()

    map(pprint, projects)
