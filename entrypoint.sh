#!/bin/bash

source /exec/evo.sh

# Check if one of the script's directories exists
if [[ -d "/shared-volume/graphdb/scripts/on_first_run"  ||  -d "/shared-volume/graphdb/scripts/on_each_run" ]]; then
    # Running first graphdb and saving its PID
    /graphdb/bin/graphdb "$1" "$2" &
    pid=$!
    sleep 20
  # Checking if it's the first run
  echo "Checking if it's the first run ..."
  if [ "$count" = 0 ]; then
    echo "It's the first run !"
      # Checking if there are files in the on_first_run directory
    echo "Checking if on_first_run directory contains scripts ..."
    nb_files=$(find "/shared-volume/graphdb/scripts/on_first_run" -maxdepth 1 -type f -name "*.sh" | wc -l)
    echo "$nb_files" " files to execute !"
    # If there are scripts, we execute them
    if [ ! "$nb_files" = 0 ]; then
      for filename in $(find "/shared-volume/graphdb/scripts/on_first_run" -maxdepth 1 -type f -name "*.sh" | sort -V); do
        echo "Executing : " "$filename"
        bash "$filename"
      done
    fi
  else echo "Not the first run !"
  fi

  # Now checking if there are scripts to execute on each launch
  # First checking if there are files in the on_each_run directory
  echo "Checking on_each_run directory"
    nb_files=$(find "/shared-volume/graphdb/scripts/on_each_run" -maxdepth 1 -type f -name "*.sh" | wc -l)
  echo $nb_files " files to execute !"
  # If there are scripts, we execute them
  if [ ! "$nb_files" = 0 ]; then
    for filename in $(find "/shared-volume/graphdb/scripts/on_each_run" -maxdepth 1 -type f -name "*.sh" | sort -V); do
      echo "Executing : " "$filename"
      bash "$filename"
    done
  fi
fi

# Stopping graphdb and relaunching it to attach it to the cmd
kill $pid
count=$((count+1))

sed -r -i "s/count=([[:graph:]]+)/count=$count/" /exec/evo.sh
echo "Running GraphDB ..."
/graphdb/bin/graphdb "$1" "$2"
