#!/usr/bin/env bash
# Career-Ops Hermes — Dashboard 服务管理
# Usage: scripts/service.sh {start|stop|restart|status|install|uninstall}
set -euo pipefail

ACTION="${1:-status}"
PLIST_NAME="com.hermes.career-ops-dashboard"
PLIST_SRC="$(cd "$(dirname "$0")" && pwd)/${PLIST_NAME}.plist"
PLIST_DST="$HOME/Library/LaunchAgents/${PLIST_NAME}.plist"
PORT="8790"
URL="http://127.0.0.1:${PORT}"
PROJECT_DIR="/Users/Dean/Workspace/Git/career-ops-hermes"

_ensure_pid_dir() {
    mkdir -p /tmp/pmo-services
}

_status() {
    echo "=== Career-Ops Hermes Dashboard ==="
    echo "  URL:       ${URL}"
    echo "  Project:   ${PROJECT_DIR}"
    echo ""

    if launchctl list | grep -q "${PLIST_NAME}"; then
        echo "  launchd:   ✅ loaded"
    else
        echo "  launchd:   ❌ not loaded"
    fi

    if curl -s -o /dev/null -w "%{http_code}" "${URL}/" 2>/dev/null | grep -q "200"; then
        echo "  HTTP:      ✅ responding on port ${PORT}"
    else
        echo "  HTTP:      ❌ not responding on port ${PORT}"
    fi

    PID_FILE="/tmp/pmo-services/career-ops-dashboard.pid"
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "  Process:   ✅ PID $PID running"
        else
            echo "  Process:   ❌ PID $PID not running (stale pid file)"
        fi
    else
        echo "  Process:   ❌ no PID file"
    fi

    echo ""
    echo "  Logs:      ${PROJECT_DIR}/webui/server.log"
}

_start() {
    _ensure_pid_dir
    echo "Starting Career-Ops Hermes Dashboard..."
    launchctl load "$PLIST_DST" 2>/dev/null || true
    launchctl start "${PLIST_NAME}" 2>/dev/null || true

    for i in $(seq 1 8); do
        if curl -s -o /dev/null "${URL}/" 2>/dev/null; then
            echo "✅ Started — ${URL}"
            return 0
        fi
        sleep 1
    done
    echo "⚠️  Started but not yet responding. Check logs: ${PROJECT_DIR}/webui/server.log"
}

_stop() {
    echo "Stopping Career-Ops Hermes Dashboard..."
    launchctl stop "${PLIST_NAME}" 2>/dev/null || true
    launchctl unload "$PLIST_DST" 2>/dev/null || true
    rm -f /tmp/pmo-services/career-ops-dashboard.pid
    echo "✅ Stopped"
}

_install() {
    _ensure_pid_dir

    cp "$PLIST_SRC" "$PLIST_DST"
    echo "✅ Installed launchd service: ${PLIST_DST}"
    echo ""
    echo "To start now:  scripts/service.sh start"
    echo "Auto-starts on next login."
}

_uninstall() {
    _stop
    rm -f "$PLIST_DST"
    echo "✅ Uninstalled launchd service"
}

_restart() {
    _stop
    sleep 1
    _start
}

case "$ACTION" in
    start)    _start ;;
    stop)     _stop ;;
    restart)  _restart ;;
    status)   _status ;;
    install)  _install ;;
    uninstall) _uninstall ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|install|uninstall}"
        exit 1
        ;;
esac
