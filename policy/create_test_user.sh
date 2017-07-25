#!/bin/bash
. /root/adminrc

load_config(){
	local configfile=config.sh
	if [[ -r "$configfile" ]]; then
		. "$configfile"
	else
		echo 'Place config.sh in CWD' >&2
		exit 1
	fi
}

roles=( service )
project_name='utility' # should this be same as service project
password='test'
load_config

dump_openrc(){
	cat <<EoF
export OS_PROJECT_NAME=$project_name
export OS_USERNAME=$testuser
export OS_PASSWORD=$password
export OS_AUTH_URL=$OS_AUTH_URL
export OS_REGION_NAME=$OS_REGION_NAME
export OS_NO_CACHE=$OS_NO_CACHE
export OS_PROJECT_DOMAIN_NAME=$OS_PROJECT_DOMAIN_NAME
export OS_USER_DOMAIN_NAME=$OS_USER_DOMAIN_NAME
export OS_IDENTITY_API_VERSION=$OS_IDENTITY_API_VERSION
export OS_IMAGE_API_VERSION=$OS_IMAGE_API_VERSION
export OS_COMPUTE_API_VERSION=$OS_COMPUTE_API_VERSION
export OS_VOLUME_API_VERSION=$OS_VOLUME_API_VERSION
EoF
}

exec 3>&1
exec 1>&2
# create the project
openstack project create --or-show $project_name
# create the user
openstack user create --or-show --project $project_name --password $password \
	$testuser
# assign the roles
for rolename in ${roles[@]}; do
	openstack role add --project $project_name --user $testuser $rolename
done
dump_openrc >&3
exec 3>&-
