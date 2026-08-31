#!/bin/sh
set -eu

: "${PORT:=8080}"
: "${QIANCRAFT_WEB_USERNAME:?QIANCRAFT_WEB_USERNAME is required}"
: "${QIANCRAFT_WEB_PASSWORD:?QIANCRAFT_WEB_PASSWORD is required}"

mkdir -p \
    /app/data/runtime/workbench \
    /app/data/runtime/tool_workspace \
    /app/runtime/auth \
    /tmp/client_body \
    /tmp/proxy_temp \
    /tmp/fastcgi_temp \
    /tmp/uwsgi_temp \
    /tmp/scgi_temp
chown -R www-data:www-data \
    /app/data/runtime \
    /app/runtime/auth \
    /tmp/client_body \
    /tmp/proxy_temp \
    /tmp/fastcgi_temp \
    /tmp/uwsgi_temp \
    /tmp/scgi_temp

password_hash="$(printf '%s' "$QIANCRAFT_WEB_PASSWORD" | openssl passwd -6 -stdin)"
printf '%s:%s\n' "$QIANCRAFT_WEB_USERNAME" "$password_hash" > /app/runtime/auth/.htpasswd
chown www-data:www-data /app/runtime/auth/.htpasswd
chmod 0600 /app/runtime/auth/.htpasswd
unset password_hash QIANCRAFT_WEB_PASSWORD

envsubst '${PORT}' \
    < /app/deploy/nginx.conf.template \
    > /app/runtime/nginx.conf

gosu www-data python -m app.tool_api --host 127.0.0.1 --port 8787 &
api_pid=$!
nginx_pid=""

(
    cd /app/web
    exec gosu www-data ./node_modules/.bin/vinext start --hostname 127.0.0.1 --port 3000
) &
web_pid=$!

cleanup() {
    if [ -n "$nginx_pid" ]; then
        kill "$nginx_pid" 2>/dev/null || true
        wait "$nginx_pid" 2>/dev/null || true
    fi
    kill "$api_pid" "$web_pid" 2>/dev/null || true
    wait "$api_pid" "$web_pid" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

attempt=0
while [ "$attempt" -lt 60 ]; do
    if node -e "Promise.all([fetch('http://127.0.0.1:8787/api/health'), fetch('http://127.0.0.1:3000/')]).then((r) => { if (r.some((x) => !x.ok)) process.exit(1) }).catch(() => process.exit(1))"; then
        break
    fi
    attempt=$((attempt + 1))
    sleep 1
done

if [ "$attempt" -ge 60 ]; then
    echo "QianCraft internal services failed to become ready" >&2
    exit 1
fi

nginx -c /app/runtime/nginx.conf -g 'daemon off;' &
nginx_pid=$!

while kill -0 "$api_pid" 2>/dev/null \
    && kill -0 "$web_pid" 2>/dev/null \
    && kill -0 "$nginx_pid" 2>/dev/null; do
    sleep 5
done

echo "QianCraft child process exited; stopping container for platform restart" >&2
exit 1
