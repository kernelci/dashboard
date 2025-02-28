#!/bin/bash

if [ -d "$DASHBOARD_BACKEND_DIR" ]; then
    cd $DASHBOARD_BACKEND_DIR
    poetry run ./manage.py \
        notifications --send --add-mailing-lists --cc gus@collabora.com \
        --action=summary
    echo "$0: finished execution at $(date)"
else
    echo "$0: \$DASHBOARD_BACKEND_DIR not set."
fi