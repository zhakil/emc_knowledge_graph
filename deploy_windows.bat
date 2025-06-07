@echo off
:: EMC知识图谱系统 - Windows一键部署脚本
:: 实用高效的自动化部署方案

title EMC知识图谱系统 - 部署向导
color 0A

echo.
echo  ========================================
echo   EMC知识图谱系统 Windows部署向导
echo  ========================================
echo.

:: 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 请以管理员身份运行此脚本
    pause
    exit /b 1
)

:: 设置变量
set PROJECT_DIR=%~dp0
set PYTHON_VERSION=3.11.0
set NODE_VERSION=18.19.0

echo 📋 开始环境检查和自动安装...

:: 检查Python
echo.
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Python未安装，正在下载安装...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe' -OutFile 'python_installer.exe'"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
    echo ✅ Python安装完成
) else (
    echo ✅ Python已安装
)

:: 检查Node.js
echo.
echo 🔍 检查Node.js环境...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Node.js未安装，正在下载安装...
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v%NODE_VERSION%/node-v%NODE_VERSION%-x64.msi' -OutFile 'node_installer.msi'"
    start /wait msiexec /i node_installer.msi /quiet
    del node_installer.msi
    echo ✅ Node.js安装完成
) else (
    echo ✅ Node.js已安装
)

:: 检查Docker Desktop
echo.
echo 🔍 检查Docker环境...
docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ⚠️  Docker未安装
    echo 💡 请手动安装Docker Desktop: https://www.docker.com/products/docker-desktop
    echo 或选择: [1] 继续安装(需要手动安装Docker) [2] 退出
    set /p choice="请选择(1/2): "
    if "%choice%"=="2" exit /b 1
) else (
    echo ✅ Docker已安装
)

:: 安装Python依赖
echo.
echo 📦 安装Python依赖...
pip install -r requirements.txt
if %errorLevel% neq 0 (
    echo ❌ Python依赖安装失败
    pause
    exit /b 1
)

:: 安装前端依赖
echo.
echo 🎨 安装前端依赖...
cd frontend
call npm install
if %errorLevel% neq 0 (
    echo ❌ 前端依赖安装失败
    pause
    exit /b 1
)
cd ..

:: 创建配置文件
echo.
echo ⚙️  创建配置文件...
if not exist .env (
    echo 📝 创建.env配置文件...
    (
        echo # EMC知识图谱系统配置
        echo EMC_SECRET_KEY=your-secret-key-here-change-in-production
        echo EMC_DEEPSEEK_API_KEY=sk-placeholder-key
        echo EMC_NEO4J_PASSWORD=Zqz112233
        echo EMC_POSTGRES_PASSWORD=Zqz112233
        echo EMC_REDIS_PASSWORD=Zqz112233
        echo EMC_ENVIRONMENT=production
        echo EMC_DEBUG=false
    ) > .env
    echo ✅ 配置文件已创建，请编辑.env文件填入实际配置
)

:: 启动数据库服务
echo.
echo 🗄️  启动数据库服务...
docker-compose up -d postgres neo4j redis
if %errorLevel% neq 0 (
    echo ❌ 数据库启动失败，请检查Docker状态
    pause
    exit /b 1
)

:: 等待数据库就绪
echo.
echo ⏳ 等待数据库初始化...
timeout /t 15 /nobreak >nul

:: 构建桌面应用
echo.
echo 📦 构建Windows桌面应用...
python scripts/build_windows_app.py
if %errorLevel% neq 0 (
    echo ❌ 桌面应用构建失败
    pause
    exit /b 1
)

:: 创建桌面快捷方式
echo.
echo 🔗 创建桌面快捷方式...
powershell -Command ^
"$WshShell = New-Object -comObject WScript.Shell; ^
$Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\EMC知识图谱系统.lnk'); ^
$Shortcut.TargetPath = '%PROJECT_DIR%build_output\EMC知识图谱系统.exe'; ^
$Shortcut.WorkingDirectory = '%PROJECT_DIR%'; ^
$Shortcut.IconLocation = '%PROJECT_DIR%desktop\assets\icon.ico'; ^
$Shortcut.Save()"

:: 完成部署
echo.
echo  ========================================
echo   🎉 部署完成！
echo  ========================================
echo.
echo  📋 部署摘要:
echo   - 桌面应用: %PROJECT_DIR%build_output\
echo   - 数据库服务: 已启动 (Postgres, Neo4j, Redis)
echo   - 配置文件: .env
echo   - 桌面快捷方式: 已创建
echo.
echo  🚀 启动方式:
echo   1. 双击桌面快捷方式 "EMC知识图谱系统"
echo   2. 或运行: %PROJECT_DIR%build_output\EMC知识图谱系统.exe
echo.
echo  🔧 管理地址:
echo   - 应用界面: http://localhost:3000
echo   - API文档: http://localhost:8000/docs
echo   - Neo4j浏览器: http://localhost:7474
echo.
echo  📚 重要提醒:
echo   1. 请在.env文件中配置DeepSeek API密钥
echo   2. 首次启动可能需要等待1-2分钟
echo   3. 如遇问题，请查看日志文件
echo.

:: 询问是否立即启动
echo 是否立即启动EMC知识图谱系统？ [Y/N]
set /p start_app="请选择: "
if /i "%start_app%"=="Y" (
    echo 🚀 启动应用中...
    start "" "%PROJECT_DIR%build_output\EMC知识图谱系统.exe"
)

echo.
echo ✅ 部署完成！按任意键退出...
pause >nul

goto :eof

:: 错误处理函数
:error
echo.
echo ❌ 部署过程中发生错误
echo 💡 请检查:
echo   1. 网络连接是否正常
echo   2. 是否以管理员身份运行
echo   3. 防火墙设置是否阻止了下载
echo.
pause
exit /b 1