from ks_auth import ks
import sys

if __name__ == '__main__':
    # some info
    from pbr.version import VersionInfo
    print('python-keystoneclient: %s' % VersionInfo('python-keystoneclient'))

    roles = ['service']
    # list out role inferences
    # print(ks.roles.list_inference_roles(name=rolename))
    # add role
    # - make them global for now
    for role in roles:
        try:
            ks.roles.create(name=role)
        except Exception, e:
            # already there
            sys.stderr.write(e.message + '\n')
