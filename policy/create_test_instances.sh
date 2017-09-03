#!/bin/bash
. /root/adminrc
roles=( Member )
project_name='user_project' # should this be same as service project
password='test'
username='standard_user'

dump_openrc(){
	cat <<EoF
export OS_PROJECT_NAME='$project_name'
export OS_USERNAME='$username'
export OS_PASSWORD='$password'
export OS_AUTH_URL=${OS_AUTH_URL:-https://openstack.bcpc.example.com:5000/v3/}
export OS_REGION_NAME='${OS_REGION_NAME:-Test-Laptop-Vagrant}'
export OS_NO_CACHE=$OS_NO_CACHE
export OS_PROJECT_DOMAIN_NAME='$OS_PROJECT_DOMAIN_NAME'
export OS_USER_DOMAIN_NAME='$OS_USER_DOMAIN_NAME'
export OS_IDENTITY_API_VERSION=$OS_IDENTITY_API_VERSION
export OS_IMAGE_API_VERSION=$OS_IMAGE_API_VERSION
export OS_COMPUTE_API_VERSION=$OS_COMPUTE_API_VERSION
export OS_VOLUME_API_VERSION=$OS_VOLUME_API_VERSION
EoF
}
# create the project
openstack project create --or-show --domain "$OS_PROJECT_DOMAIN_NAME" "$project_name"
# create the user
openstack user create --or-show --domain "$OS_USER_DOMAIN_NAME" \
  --project-domain "$OS_PROJECT_DOMAIN_NAME" \
  --project "$project_name" --password "$password" "$username"
openstack user set --password "$password" $username
# assign the roles
for rolename in "${roles[@]}"; do
  openstack role add --project "$project_name" \
    --project-domain "$OS_PROJECT_DOMAIN_NAME" \
    --user-domain "$OS_USER_DOMAIN_NAME" \
    --user "$username" "$rolename" || true
done

rc_file=user-rc
# switch creds
dump_openrc > "$rc_file"
. "$rc_file"
# create the instances
flavor='generic1.small'
image='Cirros 0.3.4 x86_64'
instances=( test_server1 )
for i in "${instances[@]}"; do
	openstack server show "$i" || \
		openstack server create --flavor "$flavor" --image "$image" --wait "$i"
done
