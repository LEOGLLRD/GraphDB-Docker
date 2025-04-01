#!/bin/sh

# First installing the dependencies with the requirements.txt file
echo "Installing the dependencies with the requirements file ..."
config/python_env/bin/pip install -r /shared-volume/python/requirements/requirements.txt
# Getting the number of times the container as been launched
source /exec/evo.sh

# Check if one of the script's directories exists
if [[ -d "/shared-volume/python/scripts/on_first_run"  ||  -d "/shared-volume/python/scripts/on_each_run" ]]; then
  # Checking if it's the first run
  echo "Checking if it's the first run ..."
  if [ "$count" = 0 ]; then
    echo "It's the first run !"
      # Checking if there are files in the on_first_run directory
    echo "Checking if on_first_run directory contains scripts ..."
    nb_files=$(find "/shared-volume/python/scripts/on_first_run" -maxdepth 1 -type f -name "*.py" | wc -l)
    echo "$nb_files" " files to execute !"
    # If there are scripts, we execute them
    if [ ! "$nb_files" = 0 ]; then
      for filename in $(find "/shared-volume/python/scripts/on_first_run" -maxdepth 1 -type f -name "*.py" | sort -V); do
        echo "Executing : " "$filename"
        /config/python_env/bin/python "$filename"
      done
    fi
  else echo "Not the first run !"
  fi

  # Now checking if there are scripts to execute on each launch
  # First checking if there are files in the on_each_run directory
  echo "Checking on_each_run directory"
    nb_files=$(find "/shared-volume/python/scripts/on_each_run" -maxdepth 1 -type f -name "*.py" | wc -l)
  echo $nb_files " files to execute !"
  # If there are scripts, we execute them
  if [ ! "$nb_files" = 0 ]; then
    for filename in $(find "/shared-volume/python/scripts/on_each_run" -maxdepth 1 -type f -name "*.py" | sort -V); do
      echo "Executing : " "$filename"
      /config/python_env/bin/python "$filename"
    done
  fi
fi

count=$((count+1))
sed -r -i "s/count=([[:graph:]]+)/count=$count/" /exec/evo.sh
echo "GraphDB initialization finished !"

echo "Launching Django ..."
/config/python_env/bin/python /django/manage.py runserver 0.0.0.0:8000

