#!/bin/sh
init_done=false
while [ $init_done = false ]; do
    . /graphdb-project/done.sh
    init=$((init))
    if [ $init = 1 ]; then
      init_done=true
    fi
done


echo "\$1 : $1, \$2 : $2, \$3 : $3"
exec /graphdb/bin/graphdb "$1" "$2" "$3"

