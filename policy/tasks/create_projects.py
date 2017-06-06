#!/usr/bin/env python
from ks_auth import ks
from ks_auth import auth_args
# RDTIBCC-983
# Satisfies Requirements:
# - create projects
# - update projects
# - delete projects

print auth_args
# Create/delete in default domain
name = 'test_project_by_name_policy'
project_domain_name = auth_args['project_domain_name']

def get_domain(name):
    res = ks.domains.list(name=name)
    return res.pop()

for domain in ks.domains.list():
    print('Using domain %s:' % domain.name)
    dom_id = domain.id
    #dom_id = get_domain(project_domain_name).id
    # identity:create_project
    proj = ks.projects.create(name=name, domain=dom_id, pvf_id='PVF_0000')
    proj_id = str(proj.id)
    print('* Created %s' % proj)
    # identity:delete_project
    ks.projects.delete(proj_id)

    name = 'test_project_by_ref_policy'
    proj = ks.projects.create(name=name, domain=dom_id, pvf_id='PVF_0000')
    print('* Created %s' % proj)
    # update the project
    desc = 'Some desc'
    # identity:update_project
    ks.projects.update(proj, description=desc)
    print('** Updated to %s:' % ks.projects.get(proj.id))
    ks.projects.delete(proj)
