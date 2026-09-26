@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==============================================
echo  创建独立 .venv 虚拟环境，安装代理依赖
echo  fastapi uvicorn requests
echo ==============================================
echo.

REM 检查python是否可用
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR：系统找不到python，请先安装Python并加入PATH
    pause
    exit /b 1
)

if exist ".venv" (
    echo .venv文件夹已存在，跳过创建虚拟环境
) else (
    echo 正在创建 .venv 虚拟环境...
    python -m venv .venv
)

echo 激活虚拟环境并安装依赖...
call .venv\Scripts\activate.bat
pip install fastapi uvicorn requests

echo.
echo ✅ 完成！.venv准备就绪
echo 启动代理命令： .venv\Scripts\python.exe aivis_proxy.py
echo.
pause