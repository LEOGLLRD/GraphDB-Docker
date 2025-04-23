#!/bin/bash

# 1 : [user_in_container]
# 2 : [versions] graphdb_python
# 3 : [container_name]
# 4 : [create_users_with_pattern]
# 5 : [number_of_users]
# 6 : [new_users_pattern]
# 7 : [users_credentials]
# 8 : [admin_password]

# Setting default values for optional arguments
user_in_container="graphdb" # u
versions="10.6.4_3.12" # v
container_name="graphdb" # i
number_of_users=1 # n
new_users_pattern="user#" # p


while getopts ":u:v:i:c:n:p:a:" flag
    do
             case "${flag}" in
                    u) user_in_container=${OPTARG};;
                    v) versions=${OPTARG};;
                    c) container_name=${OPTARG};;
                    n) number_of_users=${OPTARG};;
                    p) new_users_pattern=${OPTARG};;
             esac
    done


graphdb_version=$(echo "$versions" | cut -d '_' -f1)
python_version=$(echo "$versions" | cut -d '_' -f2)

# Creating the folder containing all the required files and folders to create the stack
mkdir -p ./LEOGLLRD-graphdb
branch="several-services-dockercompose"
project="GraphDB-Docker"
curl -L -o ./LEOGLLRD-graphdb/graphdb.zip https://github.com/LEOGLLRD/GraphDB-Docker/archive/refs/heads/several-services-dockercompose.zip
unzip ./LEOGLLRD-graphdb/graphdb.zip -d ./LEOGLLRD-graphdb
rm ./LEOGLLRD-graphdb/graphdb.zip
echo "Everything required is downloaded."

# Modifying the env vars
ENV_FILE="./LEOGLLRD-graphdb/$project-$branch/vars.env"
VAR="NUMBER_OF_USERS"
VALUE=$number_of_users
sed -i "s|^$VAR=.*|$VAR=$VALUE|" "$ENV_FILE"
VAR="NEW_USERS_PATTERN"
VALUE=$new_users_pattern
sed -i "s|^$VAR=.*|$VAR=$VALUE|" "$ENV_FILE"

echo "Setting up the docker environment ..."
docker volume create "shared-volume"
echo "Volume created !"
echo "Copying the required files to the volume by using a temporary container ..."
docker container create --name temporary -v shared-volume:/shared-volume busybox
docker cp ./LEOGLLRD-graphdb/$project-$branch/graphdb-project temporary:/shared-volume/
echo "Files copied !"
docker rm temporary
echo "Temporary container deleted !"
echo "Running docker compose up ..."


docker compose -f "./LEOGLLRD-graphdb/$project-$branch/docker-compose.yml" up
