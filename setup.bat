@echo off
echo ========================================
echo   Suricata规则生成工具 - 自动部署
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未添加到PATH
    echo 请先安装Python 3.8+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/6] 检测Python版本...
python --version

echo.
echo [2/6] 创建虚拟环境...
if exist .venv (
    echo 虚拟环境已存在，跳过创建
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo [错误] 虚拟环境创建失败
        echo 请检查Python安装是否完整
        pause
        exit /b 1
    )
    echo 虚拟环境创建成功
)

echo.
echo [3/6] 激活虚拟环境...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

echo.
echo [4/6] 升级pip...
python -m pip install --upgrade pip

echo.
echo [5/6] 安装依赖包...
pip install -r backend\requirements.txt
if errorlevel 1 (
    echo.
    echo [警告] 依赖安装失败，尝试使用国内镜像...
    pip install -r backend\requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
)

echo.
echo [6/6] 配置环境变量...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo .env 文件已创建，请编辑配置API密钥
    ) else (
        echo [警告] .env.example 文件不存在
    )
) else (
    echo .env 文件已存在，跳过创建
)

echo.
echo ========================================
echo   部署完成！
echo ========================================
echo.
echo 下一步操作：
echo 1. 编辑 .env 文件，配置您的AI_API_KEY
echo 2. 运行 start_all.bat 启动服务
echo.
echo 提示：如需重新部署，请先删除 .venv 目录
echo.
pause
