#!/bin/bash
# Career-Ops Hermes — 独立 WebUI 启动器 (launchd 管理)
# launchd 调用此脚本，exec 替换进程映像后由 launchd 守护
set -euo pipefail

eval "$(/opt/anaconda3/bin/conda shell.bash hook 2>/dev/null)"
conda activate hermes

PROJECT_DIR="/Users/Dean/Workspace/Git/hermes-webui"
PID_FILE="/tmp/pmo-services/career-ops-hermes-webui.pid"
STATE_DIR="$HOME/.hermes/webui-career-ops"

cd "$PROJECT_DIR"

# 写入 PID 文件
echo $$ > "$PID_FILE"

# 确保状态目录存在
mkdir -p "$STATE_DIR/sessions"

# 锁定 workspace 到 career-ops-hermes 项目目录
echo "/Users/Dean/Workspace/Git/career-ops-hermes" > "$STATE_DIR/last_workspace.txt"

export HERMES_WEBUI_AGENT_DIR="/Users/Dean/Workspace/Git/hermes-agent"
export HERMES_WEBUI_HOST="127.0.0.1"
export HERMES_WEBUI_PORT="8790"
export HERMES_WEBUI_STATE_DIR="$STATE_DIR"

exec python server.py
