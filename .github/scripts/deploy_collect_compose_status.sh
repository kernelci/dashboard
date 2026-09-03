#!/bin/sh
set -u

compose_file=${1:-docker-compose.yml}
failed=0

printf '| Service | Container | State | Health | Restarts | Image |\n'
printf '| --- | --- | --- | --- | ---: | --- |\n'

services=$(docker compose -f "$compose_file" config --services) || exit 1
for service in $services; do
    id=$(docker compose -f "$compose_file" ps -aq "$service")
    if [ -z "$id" ]; then
        printf '| %s | - | missing | none | - | - |\n' "$service"
        failed=1
        continue
    fi

    row=$(docker inspect --format \
        '{{index .Config.Labels "com.docker.compose.service"}}|{{.Name}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}|{{.RestartCount}}|{{.Config.Image}}|{{.State.ExitCode}}' \
        "$id") || {
        failed=1
        continue
    }

    IFS='|' read -r svc name state health restarts image exit_code <<EOF
$row
EOF
    printf '| %s | %s | %s | %s | %s | %s |\n' "$svc" "$name" "$state" "$health" "$restarts" "$image"

    if [ "$state" != "running" ] && [ "$exit_code" != "0" ]; then
        failed=1
    fi
done

exit "$failed"
