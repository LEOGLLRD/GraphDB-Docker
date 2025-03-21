#!/bin/bash

# 1 : [user_in_container]
# 2 : [graphdb_version]
# 3 : [container_name]
# 4 : [create_users_with_pattern]
# 5 : [number_of_users]
# 6 : [new_users_pattern]
# 7 : [users_credentials]
# 8 : [admin_password]
# 9 : [-v] verbosity

# Setting default values for optional arguments
user_in_container=${1:-"graphdb"}
graphdb_version=${2:-10.6.4}
container_name=${3:-"graphdb"}
create_users_with_pattern=${4:-"none"}
number_of_users=${5:-1}
new_users_pattern=${6:-"user#"}
users_credentials=${7:-"none"}
admin_password=${8:-"root"}


function print_arguments_required() {
echo "missing or incorrectly filled in argument : $1 !"

}


echo "Checking if the required arguments are given ..."

# Checking all the required arguments are given
# Checking the create_users_with_pattern argument. Must be "true" or "false"
if [ "$create_users_with_pattern" == none ] || [[  "$create_users_with_pattern" != true &&  "$create_users_with_pattern" != false ]] ; then
  print_arguments_required "create_users_with_pattern"
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
echo "Trying to create the Dockerfile ... "

# Creating the Dockerfile
mkdir -p ./generated
touch ./generated/Dockerfile
echo "" > ./generated/Dockerfile
# Writing into Dockerfile
echo "FROM eclipse-temurin:11-jdk-noble" >> ./generated/Dockerfile
echo "ARG version=$graphdb_version" >> ./generated/Dockerfile
echo "ARG download_url=\"https://maven.ontotext.com/repository/owlim-releases/com/ontotext/graphdb/graphdb/\${version}/graphdb-\${version}-dist.zip\"" >> ./generated/Dockerfile
echo "ARG download_url_checksum=\"\${download_url}.md5\"" >> ./generated/Dockerfile

echo "RUN apt-get update && apt-get install -u unzip && apt-get install -y python3 python3-pip python3.12-venv net-tools less && python3 -m venv /config/graphdb/python_env_graphdb" >> ./generated/Dockerfile

echo "RUN adduser $user_in_container" >> ./generated/Dockerfile

echo "RUN curl -fsSL \"\${download_url}\" > graphdb-\${version}-dist.zip && bash -c 'md5sum -c - <<<\"\$(curl -fsSL \${download_url_checksum})  graphdb-\${version}-dist.zip\"' && unzip graphdb-\${version}-dist.zip && rm -f graphdb-\${version}-dist.zip && mkdir -p /exec && chmod -R 755 /exec " >> ./generated/Dockerfile

echo "RUN mv graphdb-\${version} graphdb && chown -R $user_in_container /graphdb && chown -R $user_in_container /exec && mkdir \"/opt/graphdb\" && chown -R $user_in_container /opt/graphdb && mkdir -p \"/shared-volume/graphdb\" && chown -R $user_in_container /shared-volume/graphdb && mkdir -p /config/graphdb && chown -R $user_in_container /config/graphdb" >> ./generated/Dockerfile

echo "COPY entrypoint.sh evo.sh /exec/" >> ./generated/Dockerfile

echo "USER $user_in_container" >> ./generated/Dockerfile

echo "ENTRYPOINT [\"/exec/entrypoint.sh\"]" >> ./generated/Dockerfile

echo "CMD [\"-Dgraphdb.home=/opt/graphdb/home\", \"-Dgraphdb.distribution=docker\"]" >> ./generated/Dockerfile

echo "EXPOSE 7200" >> ./generated/Dockerfile
echo "EXPOSE 7300" >> ./generated/Dockerfile

echo "Dockerfile created !"

echo "Creating the docker-compose file ..."
# Creating the docker-compose file
touch ./generated/docker-compose.yml
echo "" > ./generated/docker-compose.yml
# Writing into docker-compose.yml
echo "services:" >> ./generated/docker-compose.yml
echo "  graphdb:" >> ./generated/docker-compose.yml
echo "    container_name: $container_name" >> ./generated/docker-compose.yml
echo "    build:" >> ./generated/docker-compose.yml
echo "      dockerfile: Dockerfile" >> ./generated/docker-compose.yml
echo "    ports:" >> ./generated/docker-compose.yml
echo "      - \"0:7200\"" >> ./generated/docker-compose.yml
echo "    volumes:" >> ./generated/docker-compose.yml
echo "      - \"shared-volume:/shared-volume\"" >> ./generated/docker-compose.yml
echo "volumes:" >> ./generated/docker-compose.yml
echo "  shared-volume:" >> ./generated/docker-compose.yml
echo "    name: shared-volume" >> ./generated/docker-compose.yml
echo "    external: true" >> ./generated/docker-compose.yml

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
curl -L -o ./generated/entrypoint.sh https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/entrypoint.sh
echo "entrypoint.sh downloaded !"

# Creating the required folders
echo "Creating the directories ..."
mkdir -p ./generated/graphdb
mkdir -p ./generated/graphdb/scripts
mkdir -p ./generated/graphdb/scripts/on_each_run
mkdir -p ./generated/graphdb/scripts/on_first_run
mkdir -p ./generated/graphdb/scripts/on_first_run/python
echo "Directories created !"

# Downloading the requirements.txt file
echo "Downloading requirements.txt ..."
curl -L -o ./generated/graphdb/scripts/on_first_run/python/requirements.txt https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/graphdb/scripts/on_first_run/python/requirements.txt
echo "requirements.txt downloaded !"

# Downloading the config.ini file
echo "Downloading config.ini ..."
curl -L -o ./generated/graphdb/scripts/on_first_run/python/config.ini  https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/templates/config.ini
echo "config.ini downloaded !"

# Setting it up the passed arguments
sed -i "s+\[number_of_users\]+$number_of_users+" ./generated/graphdb/scripts/on_first_run/python/config.ini
sed -i "s+\[create_users_with_pattern\]+$create_users_with_pattern+" ./generated/graphdb/scripts/on_first_run/python/config.ini
sed -i "s+\[new_users_pattern\]+$new_users_pattern+" ./generated/graphdb/scripts/on_first_run/python/config.ini
sed -i "s+\[credentials\]+$users_credentials+" ./generated/graphdb/scripts/on_first_run/python/config.ini
sed -i "s+\[admin_password\]+$admin_password+" ./generated/graphdb/scripts/on_first_run/python/config.ini

# Downloading the bash files of the on_first_run directory
echo "Downloading bash scripts ..."
curl -L -o ./generated/graphdb/scripts/on_first_run/1_python_env_setup.sh https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/graphdb/scripts/on_first_run/1_python_env_setup.sh
curl -L -o ./generated/graphdb/scripts/on_first_run/2_python_env_scripts.sh https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/graphdb/scripts/on_first_run/2_run_python_scripts.sh
echo "Bash scripts downloaded !"


# Downloading the python files
echo "Downloading python scripts ..."
curl -L -o ./generated/graphdb/scripts/on_first_run/python/1_enable_security.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/graphdb/scripts/on_first_run/python/1_enable_security.py
curl -L -o ./generated/graphdb/scripts/on_first_run/python/2_change_admin_credentials.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/graphdb/scripts/on_first_run/python/2_change_admin_credentials.py
curl -L -o ./generated/graphdb/scripts/on_first_run/python/3_create_repo.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/graphdb/scripts/on_first_run/python/3_create_repo.py
curl -L -o ./generated/graphdb/scripts/on_first_run/python/4_create_user.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/graphdb/scripts/on_first_run/python/4_create_user.py
curl -L -o ./generated/graphdb/scripts/on_first_run/python/5_setup_users_access.py https://raw.githubusercontent.com/LEOGLLRD/GraphDB-Docker/refs/heads/main/graphdb/scripts/on_first_run/python/5_setup_users_access.py
echo "Python scripts downloaded !"

echo "Everything that is required is downloaded."
echo "Setting up the docker environment ..."
docker volume create "shared-volume"
echo "Volume created !"
echo "Copying the required files to the volume by using a temporary container ..."
docker container create --name temporary -v shared-volume:/shared-volume busybox
docker cp ./generated/graphdb temporary:/shared-volume/
echo "Files copied !"
docker rm temporary
echo "Temporary container deleted !"
echo "Running docker compose up ..."

docker compose -f ./generated/docker-compose.yml up
