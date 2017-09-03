#!/bin/bash
# Do the setup
hash -r
_bin="$(readlink -f $0)"
dir=${_bin%/*}

PATH=/bin:/usr/bin:/sbin:/usr/sbin:$dir

set -ex
if [[ ! -r openrc ]]; then
  set -o pipefail
  create_test_user.sh | ( tee openrc ; [[ -s openrc ]] || rm -f openrc )
fi

. /root/adminrc && python rbp.py
create_test_instances.sh
