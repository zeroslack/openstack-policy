#!/usr/bin/env python
from ks_auth import ks
# RDTIBCC-983
# Satisfies Requirements:
# - create projects
# - update projects
# - delete projects


# Create/delete in default domain
name = 'test_project_by_name_policy'
domain = 'default'
# identity:create_project
proj = ks.projects.create(name=name, domain=domain, pvf_id='PVF_0000')
proj_id = str(proj.id)
print('Created %s' % proj)
# identity:delete_project
ks.projects.delete(proj_id)

name = 'test_project_by_ref_policy'
proj = ks.projects.create(name=name, domain=domain, pvf_id='PVF_0000')
print('Created %s' % proj)
# update the project
desc = 'Some desc'
# identity:update_project
ks.projects.update(proj, description=desc)
print('Updated to %s:' % ks.projects.get(proj.id))
ks.projects.delete(proj)
