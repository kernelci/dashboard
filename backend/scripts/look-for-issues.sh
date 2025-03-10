#!/bin/bash

if [ -d "$DASHBOARD_BACKEND_DIR" ]; then
    cd $DASHBOARD_BACKEND_DIR
    poetry run ./manage.py notifications --yes --send --to gus@collabora.com --cc tales.aparecida@redhat.com --action=new_issues
    echo "$0: finished execution at $(date)"
else
    echo "$0: \$DASHBOARD_BACKEND_DIR not set."
fi