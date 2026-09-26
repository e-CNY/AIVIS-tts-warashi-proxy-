#!/usr/bin/env bash
set -euo pipefail

# 脚本所在目录（项目根目录）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "${SCRIPT_DIR}"

echo "============================================================
  启动 AivisSpeech Proxy代理服务（新终端窗口）
============================================================
"

# 新开一个Terminal窗口运行代理：uv run python aivis_proxy.py
osascript -e 'tell application "Terminal"
    do script "cd \"'"${SCRIPT_DIR}"'\" && uv run python aivis_proxy.py"
end tell'

sleep 3

echo "============================================================
  启动 Warashi start‑companion.command（新终端窗口）
============================================================
"

# 新开终端运行原版 start‑companion.command
osascript -e 'tell application "Terminal"
    do script "cd \"'"${SCRIPT_DIR}"'\" && ./start‑companion.command"
end tell'

echo "全部启动命令已下发！"
echo "不要关闭两个终端窗口！"
echo ""
read -r -p "按回车退出此启动器…"