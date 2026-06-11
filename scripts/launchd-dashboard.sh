#!/bin/bash
# Career-Ops Hermes — 独立 Dashboard 启动器 (launchd 管理)
# 使用自带 Python 服务，无需 Hermes WebUI
set -euo pipefail

eval "$(/opt/anaconda3/bin/conda shell.bash hook 2>/dev/null)"
conda activate hermes

PROJECT_DIR="/Users/Dean/Workspace/Git/career-ops-hermes"
PID_FILE="/tmp/pmo-services/career-ops-dashboard.pid"

cd "$PROJECT_DIR"

# 写入 PID 文件
echo $$ > "$PID_FILE"

exec python3 webui/server.py --port 8790 --project-dir "$PROJECT_DIR"
