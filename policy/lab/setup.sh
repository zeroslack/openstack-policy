#!/bin/bash
# Do the setup
hash -r
_bin="$(readlink -f $0)"
dir=${_bin%/*}

PATH=/bin:/usr/bin:/sbin:/usr/sbin:$dir

set -x 
create_projects.py
add_roles.py
