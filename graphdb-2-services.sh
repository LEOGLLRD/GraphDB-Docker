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
create_users_with_pattern="none" # c
number_of_users=1 # n
new_users_pattern="user#" # p
users_credentials="user1,user1" # (à enlever)
admin_password="root" # a


while getopts ":u:v:i:c:n:p:a:" flag
    do
             case "${flag}" in
                    u) user_in_container=${OPTARG};;
                    v) versions=${OPTARG};;
                    i) container_name=${OPTARG};;
                    c) create_users_with_pattern=${OPTARG};;
                    n) number_of_users=${OPTARG};;
                    p) new_users_pattern=${OPTARG};;
                    a) admin_password=${OPTARG};;
             esac
    done

function print_arguments_required() {
echo "missing or incorrectly filled in argument : $1 !"

}


echo "Checking if the required arguments are given ..."

# Checking all the required arguments are given
# Checking the create_users_with_pattern argument. Must be "true" or "false"
if [ "$create_users_with_pattern" == none ] || [[  "$create_users_with_pattern" != true &&  "$create_users_with_pattern" != false ]] ; then
  print_arguments_required "create_users_with_pattern"
  echo "$create_users_with_pattern"
  echo "test"
  exit 1
fi

if [ "$create_users_with_pattern" == false ]; then
    # If create_users_with_pattern is set to false, we must check that users_credentials is set
    if [ "$users_credentials" = "none" ] ; then
      print_arguments_required "users_credentials"
      exit 1
    fi
fi

echo "Arguments are given !"


graphdb_version=$(echo "$versions" | cut -d '_' -f1)
python_version=$(echo "$versions" | cut -d '_' -f2)

echo "Creating the Dockerfile-graphdb ... "

# Creating the Dockerfile-graphdb
mkdir -p ./generated
touch ./generated/Dockerfile-graphdb
echo "" > ./generated/Dockerfile-graphdb
# Writing into Dockerfile
echo "FROM eclipse-temurin:11-jdk-noble" >> ./generated/Dockerfile-graphdb
echo "ARG version=$graphdb_version" >> ./generated/Dockerfile-graphdb
echo "ARG download_url=\"https://maven.ontotext.com/repository/owlim-releases/com/ontotext/graphdb/graphdb/\${version}/graphdb-\${version}-dist.zip\"" >> ./generated/Dockerfile-graphdb
echo "ARG download_url_checksum=\"\${download_url}.md5\"" >> ./generated/Dockerfile-graphdb

echo "RUN apt-get update && apt-get install -u unzip" >> ./generated/Dockerfile-graphdb

echo "RUN adduser $user_in_container" >> ./generated/Dockerfile-graphdb

echo "RUN curl -fsSL \"\${download_url}\" > graphdb-\${version}-dist.zip && bash -c 'md5sum -c - <<<\"\$(curl -fsSL \${download_url_checksum})  graphdb-\${version}-dist.zip\"' && unzip graphdb-\${version}-dist.zip && rm -f graphdb-\${version}-dist.zip" >> ./generated/Dockerfile-graphdb

echo "RUN mv graphdb-\${version} graphdb && chown -R $user_in_container /graphdb && mkdir \"/opt/graphdb\" && chown -R $user_in_container /opt/graphdb" >> ./generated/Dockerfile-graphdb



echo "USER $user_in_container" >> ./generated/Dockerfile-graphdb

echo "ENTRYPOINT [\"/graphdb/bin/graphdb\"]" >> ./generated/Dockerfile-graphdb

echo "CMD [\"-Dgraphdb.home=/opt/graphdb/home\", \"-Dgraphdb.distribution=docker\"]" >> ./generated/Dockerfile-graphdb

echo "EXPOSE 7200" >> ./generated/Dockerfile-graphdb
echo "EXPOSE 7300" >> ./generated/Dockerfile-graphdb

echo "Dockerfile-graphdb created !"

echo "Creating the Dockerfile-python ..."
# Creating the Dockerfile-python
touch ./generated/Dockerfile-python
echo "" > ./generated/Dockerfile-python

echo "FROM python:$python_version-alpine" >> ./generated/Dockerfile-python
echo "RUN mkdir -p /exec && mkdir -p /shared-volume/graphdb-project/python && mkdir -p /config && python -m venv /config/python_env" >> ./generated/Dockerfile-python
echo "RUN adduser -D python && echo \"python:python\" | chpasswd" >> ./generated/Dockerfile-python
echo "RUN chown -R python /config/python_env && mkdir -p \"/shared-volume/graphdb-project/python\" && chmod 551 /shared-volume/graphdb-project/python && chown -R python /exec" >> ./generated/Dockerfile-python
echo "COPY entrypoint.sh evo.sh /exec/" >> ./generated/Dockerfile-python
echo "USER python" >> ./generated/Dockerfile-python
echo "ENTRYPOINT [\"/exec/entrypoint.sh\"]" >> ./generated/Dockerfile-python

echo "Dockerfile-python created !"

echo "Creating the docker-compose file ..."
# Creating the docker-compose file
touch ./generated/docker-compose.yml
echo "" > ./generated/docker-compose.yml
# Writing into docker-compose.yml
echo "services:" >> ./generated/docker-compose.yml
echo "  graphdb:" >> ./generated/docker-compose.yml
echo "    container_name: $container_name" >> ./generated/docker-compose.yml
echo "    build:" >> ./generated/docker-compose.yml
echo "      dockerfile: Dockerfile-graphdb" >> ./generated/docker-compose.yml
echo "    ports:" >> ./generated/docker-compose.yml
echo "      - \"0:7200\"" >> ./generated/docker-compose.yml
echo "    volumes:" >> ./generated/docker-compose.yml
echo "      - \"shared-volume:/shared-volume\"" >> ./generated/docker-compose.yml
echo "    networks:" >> ./generated/docker-compose.yml
echo "      - graphdbnetwork" >> ./generated/docker-compose.yml
echo "    healthcheck:" >> ./generated/docker-compose.yml
echo "      test: [ \"CMD-SHELL\", \"grep 'Started GraphDB' /opt/graphdb/home/logs/main.log\" ]" >> ./generated/docker-compose.yml
echo "      interval: 10s" >> ./generated/docker-compose.yml
echo "      timeout: 10s" >> ./generated/docker-compose.yml
echo "      retries: 3" >> ./generated/docker-compose.yml
echo "      start_period: 20s" >> ./generated/docker-compose.yml
echo "  python:" >> ./generated/docker-compose.yml
echo "    build:" >> ./generated/docker-compose.yml
echo "      dockerfile: Dockerfile-python" >> ./generated/docker-compose.yml
echo "    volumes:" >> ./generated/docker-compose.yml
echo "      - shared-volume:/shared-volume" >> ./generated/docker-compose.yml
echo "    container_name: \"python\"" >> ./generated/docker-compose.yml
echo "    networks:" >> ./generated/docker-compose.yml
echo "      - graphdbnetwork" >> ./generated/docker-compose.yml
echo "    depends_on:" >> ./generated/docker-compose.yml
echo "      - graphdb" >> ./generated/docker-compose.yml

echo "volumes:" >> ./generated/docker-compose.yml
echo "  shared-volume:" >> ./generated/docker-compose.yml
echo "    name: shared-volume" >> ./generated/docker-compose.yml
echo "    external: true" >> ./generated/docker-compose.yml
echo "networks:" >> ./generated/docker-compose.yml
echo "  graphdbnetwork:" >> ./generated/docker-compose.yml

echo "Docker-compose file created !"

echo "Creating the evo.sh file ..."
# Creating the evo.sh file
touch ./generated/evo.sh
echo "" > ./generated/evo.sh
# Writing into evo.sh
echo "#!/bin/bash" >> ./generated/evo.sh
echo "count=0" >> ./generated/evo.sh

echo "evo.sh created !"

# Downloading the entrypoint.sh file
echo "Downloading entrypoint.sh ..."
curl -L -o ./generated/entrypoint.sh https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/2-services-dockercompose/entrypoint.sh
echo "entrypoint.sh downloaded !"

# Creating the required folders
echo "Creating the directories ..."
mkdir -p ./generated/python
mkdir -p ./generated/python/requirements
mkdir -p ./generated/python/scripts
mkdir -p ./generated/python/scripts/on_each_run
mkdir -p ./generated/python/scripts/on_first_run
echo "Directories created !"

# Downloading the requirements.txt file
echo "Downloading requirements.txt ..."
curl -L -o ./generated/python/requirements/requirements.txt https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/2-services-dockercompose/python/requirements/requirements.txt
echo "requirements.txt downloaded !"

# Downloading the config.ini file
echo "Downloading config.ini ..."
curl -L -o ./generated/python/config.ini  https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/2-services-dockercompose/templates/config.ini
echo "config.ini downloaded !"

# Setting it up the passed arguments
sed -i "s+\[number_of_users\]+$number_of_users+" ./generated/python/config.ini
sed -i "s+\[create_users_with_pattern\]+$create_users_with_pattern+" ./generated/python/config.ini
sed -i "s+\[new_users_pattern\]+$new_users_pattern+" ./generated/python/config.ini
sed -i "s+\[credentials\]+$users_credentials+" ./generated/python/config.ini
sed -i "s+\[admin_password\]+$admin_password+" ./generated/python/config.ini

# Downloading the python files
echo "Downloading python scripts ..."
curl -L -o ./generated/python/scripts/on_first_run/1_enable_security.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/2-services-dockercompose/python/scripts/on_first_run/1_enable_security.py
curl -L -o ./generated/python/scripts/on_first_run/2_change_admin_credentials.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/2-services-dockercompose/python/scripts/on_first_run/2_change_admin_credentials.py
curl -L -o ./generated/python/scripts/on_first_run/3_create_repo.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/2-services-dockercompose/python/scripts/on_first_run/3_create_repo.py
curl -L -o ./generated/python/scripts/on_first_run/4_create_user.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/2-services-dockercompose/python/scripts/on_first_run/4_create_user.py
curl -L -o ./generated/python/scripts/on_first_run/5_setup_users_access.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/2-services-dockercompose/python/scripts/on_first_run/5_setup_users_access.py
echo "Python scripts downloaded !"

echo "Everything that is required is downloaded."
echo "Setting up the docker environment ..."
docker volume create "shared-volume"
echo "Volume created !"
echo "Copying the required files to the volume by using a temporary container ..."
docker container create --name temporary -v shared-volume:/shared-volume busybox
docker cp ./generated/python temporary:/shared-volume/
echo "Files copied !"
docker rm temporary
echo "Temporary container deleted !"
echo "Running docker compose up ..."

docker compose -f ./generated/docker-compose.yml up