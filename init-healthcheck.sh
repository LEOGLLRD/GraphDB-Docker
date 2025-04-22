#!/bin/sh
USER=$(stat -c '%U' "/shared-volume/graphdb-project/graphdb")
if [ "$USER" != "graphdb" ]; then
    exit 1
fi

USER=$(stat -c '%U' "/shared-volume/graphdb-project/python")
if [ "$USER" != "graphdb" ]; then
    exit 1
fi

USER=$(stat -c '%U' "/shared-volume/graphdb-project/mysql")
if [ "$USER" != "graphdb" ]; then
    exit 1
fi

exit 0