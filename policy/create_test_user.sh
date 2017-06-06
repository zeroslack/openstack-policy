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

roles=( provisioner service )
project_name='utility' # should this be same as service project
password='test'
domain='dev'
load_config

dump_openrc(){
	cat <<EoF
export OS_PROJECT_NAME=$project_name
export OS_USERNAME=$testuser
export OS_PASSWORD=$password
export OS_AUTH_URL=$OS_AUTH_URL
export OS_REGION_NAME=$OS_REGION_NAME
export OS_NO_CACHE=1
export OS_PROJECT_DOMAIN_NAME=$domain
export OS_USER_DOMAIN_NAME=default
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
export OS_COMPUTE_API_VERSION=2
export OS_VOLUME_API_VERSION=2
EoF
}

# create the project
openstack project create --domain $domain --or-show $project_name
# create the user
openstack user create --or-show --domain default --project-domain $domain --project $project_name --password $password \
	$testuser
# assign the roles
for rolename in ${roles[@]}; do
	openstack role add --project $project_name --project-domain $domain --user-domain default --user $testuser $rolename
done
dump_openrc
