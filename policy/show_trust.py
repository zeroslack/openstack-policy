#!/usr/bin/env python
from ks_auth import ks
import sys
from pprint import pprint

if __name__ == '__main__':
    try:
        trust_id = sys.argv[1]
    except IndexError:
        sys.exit('Supply a trust id')

    # Both parties to trust can view the trust
    # - without using trust-scoped authentication
    #   * impersonation=False
    trust = ks.trusts.get(trust_id)
    # For ease...
    pprint(trust.__dict__)
