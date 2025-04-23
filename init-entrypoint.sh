#!/bin/sh
# Getting the number of times the container as been launched
source /evo.sh

if [ "$count" = 0 ]; then
  echo "First run !"
  # Emptying the graphDB folders
  rm -f /shared-volume/graphdb-project/graphdb/data/*.js
  rm -r -f /shared-volume/graphdb-project/graphdb/data/repositories/*
  rm -r -f /shared-volume/graphdb-project/graphdb/data/logs/*
  rm -r -f /shared-volume/graphdb-project/graphdb/data/backups/*

fi

chown -R graphdb /shared-volume/graphdb-project/graphdb
chown -R graphdb /shared-volume/graphdb-project/python
chown -R graphdb /shared-volume/graphdb-project/mysql
echo "Initialisation finished !"
URL="http://python:8000/healthz/"
SLEEP_DELAY=10
# Checking if the config.ini is set and Django is started
condition=0
while [ $condition = 0 ];
do
    MYSQLRootPass=$(sed -nr "/^\[MYSQL\]/ { :l /^root_password[ ]*=/ { s/[^=]*=[ ]*//; p; q;}; n; b l;}" ./shared-volume/graphdb-project/python/config.ini)
    MYSQLGraphdbPass=$(sed -nr "/^\[MYSQL\]/ { :l /^graphdb_password[ ]*=/ { s/[^=]*=[ ]*//; p; q;}; n; b l;}" ./shared-volume/graphdb-project/python/config.ini)
    GraphdbAdminPass=$(sed -nr "/^\[USERS\]/ { :l /^admin_password[ ]*=/ { s/[^=]*=[ ]*//; p; q;}; n; b l;}" ./shared-volume/graphdb-project/python/config.ini)
    DjangoSecretKey=$(sed -nr "/^\[DJANGO\]/ { :l /^secret_key[ ]*=/ { s/[^=]*=[ ]*//; p; q;}; n; b l;}" ./shared-volume/graphdb-project/python/config.ini)  
    if [ "$MYSQLRootPass" = "root" ] || [ "$MYSQLGraphdbPass" = "root" ] || [ "$GraphdbAdminPass" = "root" ] || [ "$DjangoSecretKey" = "secret" ]; then
        sleep "$SLEEP_DELAY"
        continue
    fi
    STATUS_CODE=$(wget --server-response --spider "$URL" 2>&1 \
    | awk '/HTTP\// {print $2}' | head -n1)
    # echo "Status code : $STATUS_CODE"
    if [ "$STATUS_CODE" = "200" ]; then
    echo "---------------------------------"
    #echo "MySQL root user's password : $MYSQLRootPass"
    #echo "MySQL GraphDB user's password : $MYSQLGraphdbPass"
    echo "GraphDB admin user's password : $GraphdbAdminPass"
    #echo "Django secret_key : $DjangoSecretKey"
    echo "---------------------------------"
    condition=1
    else
      sleep "$SLEEP_DELAY"
    fi

done

count=$((count+1))
sed -r -i "s/count=([[:graph:]]+)/count=$count/" /evo.sh