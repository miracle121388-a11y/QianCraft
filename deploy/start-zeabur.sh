#!/bin/sh
set -eu

: "${PORT:=8080}"
: "${QIANCRAFT_WEB_USERNAME:?QIANCRAFT_WEB_USERNAME is required}"
: "${QIANCRAFT_WEB_PASSWORD:?QIANCRAFT_WEB_PASSWORD is required}"
: "${QIANCRAFT_BROWSER_SESSION_ENABLED:=true}"
: "${QIANCRAFT_BROWSER_PROFILE_DIR:=/app/data/runtime/browser-profile}"
: "${MEDIACRAWLER_PYTHON:=/opt/mediacrawler-venv/bin/python}"
: "${MEDIACRAWLER_CDP_PORT:=9222}"

browser_enabled=false
case "$(printf '%s' "$QIANCRAFT_BROWSER_SESSION_ENABLED" | tr '[:upper:]' '[:lower:]')" in
    1|true|yes|on) browser_enabled=true ;;
esac

mkdir -p \
    /app/data/runtime/lightrag_storage \
    /app/data/runtime/workbench \
    /app/data/runtime/tool_workspace \
    /app/runtime/auth \
    /tmp/client_body \
    /tmp/fastcgi_temp \
    /tmp/proxy_temp \
    /tmp/qiancraft-browser-cache \
    /tmp/qiancraft-browser-config \
    /tmp/qiancraft-xdg-runtime \
    /tmp/scgi_temp \
    /tmp/uwsgi_temp
if [ "$browser_enabled" = true ]; then
    mkdir -p "$QIANCRAFT_BROWSER_PROFILE_DIR"
fi
chown -R www-data:www-data \
    /app/data/runtime \
    /app/runtime/auth \
    /tmp/client_body \
    /tmp/fastcgi_temp \
    /tmp/proxy_temp \
    /tmp/qiancraft-browser-cache \
    /tmp/qiancraft-browser-config \
    /tmp/qiancraft-xdg-runtime \
    /tmp/scgi_temp \
    /tmp/uwsgi_temp
chmod 0700 /tmp/qiancraft-xdg-runtime
if [ "$browser_enabled" = true ]; then
    chmod 0700 "$QIANCRAFT_BROWSER_PROFILE_DIR"
    # Container hostnames change across deployments; only Chromium's stale
    # singleton locks are disposable. Login databases remain untouched.
    rm -f \
        "$QIANCRAFT_BROWSER_PROFILE_DIR/SingletonCookie" \
        "$QIANCRAFT_BROWSER_PROFILE_DIR/SingletonLock" \
        "$QIANCRAFT_BROWSER_PROFILE_DIR/SingletonSocket"
fi

if [ ! -x "$MEDIACRAWLER_PYTHON" ] \
    || ! PYTHONPATH=/app/market-intel_agent/MediaCrawler-main \
        "$MEDIACRAWLER_PYTHON" -c \
        'import httpx; from tools.cdp_browser import CDPBrowserManager' \
        > /dev/null 2>&1; then
    echo "QianCraft MediaCrawler interpreter or CDP dependencies are unavailable" >&2
    exit 1
fi

password_hash="$(printf '%s' "$QIANCRAFT_WEB_PASSWORD" | openssl passwd -6 -stdin)"
printf '%s:%s\n' "$QIANCRAFT_WEB_USERNAME" "$password_hash" > /app/runtime/auth/.htpasswd
chown www-data:www-data /app/runtime/auth/.htpasswd
chmod 0600 /app/runtime/auth/.htpasswd
unset password_hash QIANCRAFT_WEB_PASSWORD

envsubst '${PORT}' \
    < /app/deploy/nginx.conf.template \
    > /app/runtime/nginx.conf

xvfb_pid=""
openbox_pid=""
vnc_pid=""
websockify_pid=""
browser_pid=""

port_ready() {
    node -e "const net=require('net');const socket=net.createConnection({host:'127.0.0.1',port:Number(process.argv[1])});socket.setTimeout(500);socket.once('connect',()=>{socket.end();process.exit(0)});socket.once('timeout',()=>{socket.destroy();process.exit(1)});socket.once('error',()=>process.exit(1));" "$1"
}

if [ "$browser_enabled" = true ]; then
    export DISPLAY=:99
    export QIANCRAFT_INTERACTIVE_CRAWL_ALLOWED=true
    export XDG_CACHE_HOME=/tmp/qiancraft-browser-cache
    export XDG_CONFIG_HOME=/tmp/qiancraft-browser-config
    export XDG_RUNTIME_DIR=/tmp/qiancraft-xdg-runtime

    gosu www-data Xvfb "$DISPLAY" -screen 0 1440x900x24 -nolisten tcp \
        > /tmp/qiancraft-xvfb.log 2>&1 &
    xvfb_pid=$!

    attempt=0
    while [ "$attempt" -lt 30 ] && [ ! -S /tmp/.X11-unix/X99 ]; do
        attempt=$((attempt + 1))
        sleep 1
    done
    if [ ! -S /tmp/.X11-unix/X99 ]; then
        echo "QianCraft display failed to become ready" >&2
        exit 1
    fi

    gosu www-data openbox --sm-disable > /tmp/qiancraft-openbox.log 2>&1 &
    openbox_pid=$!
    gosu www-data x11vnc \
        -display "$DISPLAY" \
        -rfbport 5900 \
        -localhost \
        -forever \
        -shared \
        -nopw \
        -noxdamage \
        -repeat \
        > /tmp/qiancraft-x11vnc.log 2>&1 &
    vnc_pid=$!

    gosu www-data chromium \
        --remote-debugging-address=127.0.0.1 \
        --remote-debugging-port="$MEDIACRAWLER_CDP_PORT" \
        --remote-allow-origins="http://127.0.0.1:${MEDIACRAWLER_CDP_PORT},http://localhost:${MEDIACRAWLER_CDP_PORT}" \
        --user-data-dir="$QIANCRAFT_BROWSER_PROFILE_DIR" \
        --disk-cache-dir=/tmp/qiancraft-browser-cache/chromium \
        --password-store=basic \
        --disable-background-networking \
        --disable-breakpad \
        --disable-component-update \
        --disable-crash-reporter \
        --disable-dev-shm-usage \
        --disable-gpu \
        --disable-sync \
        --disable-features=Translate \
        --metrics-recording-only \
        --no-default-browser-check \
        --no-first-run \
        --window-size=1440,900 \
        https://www.xiaohongshu.com/explore \
        https://www.douyin.com/ \
        https://www.bilibili.com/ \
        https://weibo.com/ \
        > /tmp/qiancraft-chromium.log 2>&1 &
    browser_pid=$!

    attempt=0
    while [ "$attempt" -lt 60 ] && ! port_ready "$MEDIACRAWLER_CDP_PORT"; do
        attempt=$((attempt + 1))
        sleep 1
    done
    if ! port_ready "$MEDIACRAWLER_CDP_PORT"; then
        echo "QianCraft managed browser failed to expose its loopback CDP endpoint" >&2
        exit 1
    fi

    gosu www-data websockify \
        --web=/usr/share/novnc \
        127.0.0.1:6080 \
        127.0.0.1:5900 \
        > /tmp/qiancraft-websockify.log 2>&1 &
    websockify_pid=$!

    attempt=0
    while [ "$attempt" -lt 30 ] && ! port_ready 6080; do
        attempt=$((attempt + 1))
        sleep 1
    done
    if ! port_ready 6080; then
        echo "QianCraft protected browser gateway failed to become ready" >&2
        exit 1
    fi
else
    export QIANCRAFT_INTERACTIVE_CRAWL_ALLOWED=false
fi

gosu www-data python -m app.tool_api --host 127.0.0.1 --port 8787 &
api_pid=$!
nginx_pid=""

(
    cd /app/web
    exec gosu www-data ./node_modules/.bin/vinext start --hostname 127.0.0.1 --port 3000
) &
web_pid=$!

stop_process() {
    process_id="$1"
    if [ -n "$process_id" ]; then
        kill "$process_id" 2>/dev/null || true
        wait "$process_id" 2>/dev/null || true
    fi
}

cleanup() {
    stop_process "$nginx_pid"
    stop_process "$api_pid"
    stop_process "$web_pid"
    stop_process "$websockify_pid"
    stop_process "$browser_pid"
    stop_process "$vnc_pid"
    stop_process "$openbox_pid"
    stop_process "$xvfb_pid"
}
trap cleanup INT TERM EXIT

attempt=0
while [ "$attempt" -lt 60 ]; do
    if node -e "Promise.all([fetch('http://127.0.0.1:8787/api/health'), fetch('http://127.0.0.1:3000/')]).then((responses) => { if (responses.some((response) => !response.ok)) process.exit(1) }).catch(() => process.exit(1))"; then
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
    if [ "$browser_enabled" = true ] \
        && { ! kill -0 "$xvfb_pid" 2>/dev/null \
            || ! kill -0 "$openbox_pid" 2>/dev/null \
            || ! kill -0 "$vnc_pid" 2>/dev/null \
            || ! kill -0 "$websockify_pid" 2>/dev/null \
            || ! kill -0 "$browser_pid" 2>/dev/null; }; then
        break
    fi
    sleep 5
done

echo "QianCraft child process exited; stopping container for platform restart" >&2
exit 1
