#!/usr/bin/env python
from __future__ import print_function
from ks_auth import ks
import sys
from pprint import pprint

if __name__ == '__main__':
    user_id = ks.auth.client.get_user_id()
    user_type = ['trustor', 'trustee']
    for d in user_type:
        args = {}
        name = '%s_user' % d
        args[name] = user_id
        print('Trusts as %s' % d)
        trusts = ks.trusts.list(**args)
        map(print, trusts)
