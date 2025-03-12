#!/bin/bash
path="/extern_data/data/scripts/on_first_run/python"
error=0
# Then, run all the scripts
for filename in $(find "$path" -maxdepth 1 -type f -name "*.py" | sort -V); do
  echo "Executing : " "$filename"
  /tmp/env_graphdb/bin/python "$filename"
  exit_code=$?
  if [ $exit_code = 0 ]; then
    echo "$filename executed successfully !"
  else
    echo "An error occurred !"
    error=1
  fi
done
exit $error