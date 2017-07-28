#!/bin/bash 
hash -r

# create the instances
flavor='generic1.small'
image='Cirros 0.3.4 x86_64'
instances=( test_server1 )
for i in ${instances[@]}; do
        openstack server show $i || \
                openstack server create --flavor $flavor --image "$image" --wait $i
done
