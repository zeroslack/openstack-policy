from ks_auth import ks

if __name__ == '__main__':
    # some info
    from pbr.version import VersionInfo
    print('python-keystoneclient: %s' % VersionInfo('python-keystoneclient'))

    rolename = 'provisioner'
    # list out role inferences
    # print(ks.roles.list_inference_roles(name=rolename))
    # add role
    # - make them global for now
    try:
        ks.roles.create(name=rolename)
    except:
        # already there
        pass 
