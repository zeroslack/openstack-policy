#!/bin/bash
. /root/adminrc
roles=( Member )
project_name='user_project' # should this be same as service project
password='test'
username='standard_user'

dump_openrc(){
	cat <<EoF
export OS_PROJECT_NAME=$project_name
export OS_USERNAME=$username
export OS_PASSWORD=$password
export OS_AUTH_URL=https://openstack.bcpc.example.com:5000/v3/
export OS_REGION_NAME=Test-Laptop-Vagrant
export OS_NO_CACHE=1
export OS_PROJECT_DOMAIN_NAME=default
export OS_USER_DOMAIN_NAME=default
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
export OS_COMPUTE_API_VERSION=2
export OS_VOLUME_API_VERSION=2
EoF
}
# create the project
openstack project create --or-show $project_name
# create the user
openstack user create --or-show --project $project_name --password $password \
	$username
# assign the roles
for rolename in ${roles[@]}; do
	openstack role add --project $project_name --user $username $rolename
done

# switch creds
eval $(dump_openrc)
# create the instances
flavor='generic1.small'
image='Cirros 0.3.4 x86_64'
openstack server create --flavor $flavor --image "$image" --wait test_server1
