#!/bin/sh

# Checking if MySQL is launched
mysql_done=false
while [ $mysql_done = false ]; do
    source /graphdb-project//done.sh
    mysql=$((mysql))
    if [ $mysql = 1 ]; then
      mysql_done=true
    fi
done

# Checking if GraphDB is launched
graphdb_done=false
while [ $graphdb_done = false ]; do
    URL="http://graphdb:7200/rest/repositories/"
    STATUS_CODE=$(wget --server-response --spider "$URL" 2>&1 \
        | awk '/HTTP\// {print $2}' | head -n1)
    echo "STATUS_CODE : $STATUS_CODE"
    if [ "$STATUS_CODE" = "200" ] || [ "$STATUS_CODE" = "401" ]; then
        graphdb_done=true
    fi
    continue
done

# First installing the dependencies with the requirements.txt file
echo "Installing the dependencies with the requirements file ..."
config/python_env/bin/pip install -r /graphdb-project/python/requirements/requirements.txt
# Getting the number of times the container as been launched
source /exec/evo.sh

# Setting the valus of NUMBER_OF_USERS and NEW_USERS_PATTERN ENVIRONMENT VARIABLES in config.ini
echo "Setting the config.ini file ..."
ini_file="/graphdb-project/python/config.ini"
section="USERS"
key="number_of_users"
new_value="$NUMBER_OF_USERS"
sed -i "/^\[$section\]/,/^\[/ s/^$key *= *.*/$key = $new_value/" "$ini_file"
key="new_users_pattern"
new_value="$NEW_USERS_PATTERN"
sed -i "/^\[$section\]/,/^\[/ s/^$key *= *.*/$key = $new_value/" "$ini_file"
# Check if one of the script's directories exists
if [[ -d "/graphdb-project/python/scripts/on_first_run"  ||  -d "/graphdb-project/python/scripts/on_each_run" ]]; then
  # Checking if it's the first run
  echo "Checking if it's the first run ..."
  if [ "$count" = 0 ]; then
    echo "It's the first run !"
      # Checking if there are files in the on_first_run directory
    echo "Checking if on_first_run directory contains scripts ..."
    nb_files=$(find "/graphdb-project/python/scripts/on_first_run" -maxdepth 1 -type f -name "*.py" | wc -l)
    echo "$nb_files" " files to execute !"
    # If there are scripts, we execute them
    if [ ! "$nb_files" = 0 ]; then
      for filename in $(find "/graphdb-project/python/scripts/on_first_run" -maxdepth 1 -type f -name "*.py" | sort -V); do
        echo "Executing : " "$filename"
        /config/python_env/bin/python "$filename"
      done
    fi
  else echo "Not the first run !"
  fi

  # Now checking if there are scripts to execute on each launch
  # First checking if there are files in the on_each_run directory
  echo "Checking on_each_run directory"
    nb_files=$(find "/graphdb-project/python/scripts/on_each_run" -maxdepth 1 -type f -name "*.py" | wc -l)
  echo "$nb_files" " files to execute !"
  # If there are scripts, we execute them
  if [ ! "$nb_files" = 0 ]; then
    for filename in $(find "/graphdb-project//python/scripts/on_each_run" -maxdepth 1 -type f -name "*.py" | sort -V); do
      echo "Executing : " "$filename"
      /config/python_env/bin/python "$filename"
    done
  fi
fi

count=$((count+1))
sed -r -i "s/count=([[:graph:]]+)/count=$count/" /exec/evo.sh
echo "GraphDB initialization finished !"

echo "Launching Django ..."
nohup /config/python_env/bin/python /django/manage.py runserver 0.0.0.0:8000 &
pid=$!
/config/python_env/bin/python /django/manage.py makemigrations
/config/python_env/bin/python /django/manage.py migrate
kill $pid
/config/python_env/bin/python /django/manage.py runserver 0.0.0.0:8000

