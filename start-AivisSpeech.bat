@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==============================================
echo  启动 AivisSpeech Proxy代理服务（新窗口）
echo ==============================================
start "Aivis‑Proxy" cmd /k ".venv\Scripts\activate.bat & python aivis_proxy.py"

timeout /t 3 /nobreak >nul

echo ==============================================
echo  启动 Open‑LLM‑VTuber start-companion.bat
echo ==============================================
:: 全部使用键盘英文短横杠 - ，并且强制切工作目录
start "VTuber‑Companion" cmd /k "cd /d ""%~dp0"" && call start-companion.bat"

echo 全部启动命令已下发！
echo 不要关闭两个黑色控制台窗口！
pause