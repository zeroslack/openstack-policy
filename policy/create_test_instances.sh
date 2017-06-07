#!/bin/bash
. /root/adminrc
roles=( Member )
project_name='user_project' # should this be same as service project
password='test'
username='standard_user'
project_domain='dev'

dump_openrc(){
	cat <<EoF
export OS_PROJECT_NAME=$project_name
export OS_USERNAME=$username
export OS_PASSWORD=$password
export OS_AUTH_URL=$OS_AUTH_URL
export OS_REGION_NAME=$OS_REGION_NAME
export OS_NO_CACHE=1
export OS_PROJECT_DOMAIN_NAME=$project_domain
export OS_USER_DOMAIN_NAME=default
export OS_IDENTITY_API_VERSION=3
export OS_IMAGE_API_VERSION=2
export OS_COMPUTE_API_VERSION=2
export OS_VOLUME_API_VERSION=2
EoF
}

get_domain_id(){
	local name="$1"

	if [[ -z "$name" ]]; then return 1 ; fi
	local res=$(
		eval $(openstack domain show -fshell $name)
		echo $id
	)
	[[ -z "$res" ]] && return 1
	echo $res
}

domain_id=$(get_domain_id $project_domain)
# create the project
openstack project create --or-show --domain=$project_domain $project_name
# create the user
#openstack user create --or-show --project-domain=$domain_id --project $project_name --password $password \
openstack user create --or-show --domain default --project-domain=$project_domain --project $project_name --password $password \
	$username
# assign the roles
for rolename in ${roles[@]}; do
	openstack role add --project $project_name --project-domain=$project_domain --user-domain default --user $username $rolename
done

# switch creds
eval $(dump_openrc)
dump_openrc
# create the instances
flavor='m1.tiny'
image='Cirros 0.3.4 x86_64'
openstack server create --flavor $flavor --image "$image" --wait test_server1
