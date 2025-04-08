#!/bin/bash
# Copyright Broadcom, Inc. All Rights Reserved.
# SPDX-License-Identifier: APACHE-2.0

# Getting the number of times the container as been launched
source /exec/evo.sh

# shellcheck disable=SC1091

set -o errexit
set -o nounset
set -o pipefail
# set -o xtrace # Uncomment this line for debugging purposes

# Load libraries
. /opt/bitnami/scripts/libbitnami.sh
. /opt/bitnami/scripts/libmysql.sh

# Load MySQL environment variables
. /opt/bitnami/scripts/mysql-env.sh

print_welcome_page

# We add the copy from default config in the entrypoint to not break users
# bypassing the setup.sh logic. If the file already exists do not overwrite (in
# case someone mounts a configuration file in /opt/bitnami/mysql/conf)
debug "Copying files from $DB_DEFAULT_CONF_DIR to $DB_CONF_DIR"
cp -nfr "$DB_DEFAULT_CONF_DIR"/. "$DB_CONF_DIR"

if [[ "$1" = "/opt/bitnami/scripts/mysql/run.sh" ]]; then
    info "** Starting MySQL setup **"
    /opt/bitnami/scripts/mysql/setup.sh
    info "** MySQL setup finished! **"

fi

if [ "$count" = 0 ]; then
echo "First run of the MySQL container !"
exec "$@" &
pid=$!

sleep 10
LENGTH=8

echo "Generating new password for root user ..."
PASSWORD=$(date +%s%N | sha256sum | base64 | tr -dc 'A-Za-z0-9' | head -c $LENGTH)

echo "Generated root Password : $PASSWORD"
query="ALTER USER 'root'@'%' IDENTIFIED BY '$PASSWORD';"
mysql -u root -p'root' -e "$query"
kill $pid
ini_file="/shared-volume-python/config.ini"
section="MYSQL"
key="root_password"
new_value="$PASSWORD"
sed -i "/^\[$section\]/,/^\[/ s/^$key *= *.*/$key = $new_value/" "$ini_file"
echo "Password changed !"
fi

count=$((count+1))
sed -r -i "s/count=([[:graph:]]+)/count=$count/" /exec/evo.sh
exec "$@"
