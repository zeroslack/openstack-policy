#!/usr/bin/env python
from keystoneclient import discover

def _do_discover(session, **kwargs):
    d = discover.Discover(session=session, **kwargs)
    return d

if __name__ == '__main__':
    from ka_auth import sess, auth
    from pprint import pprint

    kwargs = {}
    kwargs['auth'] = auth
    pprint(auth)


