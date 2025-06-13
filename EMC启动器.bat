@echo off
chcp 65001 >nul
title EMC知识图谱系统启动器

:menu
cls
echo.
echo ████████████████████████████████████████████████
echo █          EMC知识图谱系统启动器              █
echo ████████████████████████████████████████████████
echo.
echo 请选择启动方式:
echo.
echo [1] 🖥️  启动桌面应用 (推荐)
echo [2] 🌐 启动Web服务
echo [3] 🎨 打开演示页面
echo [4] 🐳 Docker部署
echo [5] 📖 查看文档
echo [6] 🚪 退出
echo.
set /p choice=请输入选项 (1-6): 

if "%choice%"=="1" goto desktop_app
if "%choice%"=="2" goto web_service
if "%choice%"=="3" goto demo_page
if "%choice%"=="4" goto docker_deploy
if "%choice%"=="5" goto view_docs
if "%choice%"=="6" goto exit
goto menu

:desktop_app
cls
echo 🖥️ 启动桌面应用...
echo.
if exist "emc_app.py" (
    python emc_app.py
) else if exist "EMC知识图谱系统.exe" (
    start "" "EMC知识图谱系统.exe"
) else (
    echo ❌ 找不到桌面应用文件
    echo 请确保 emc_app.py 或 EMC知识图谱系统.exe 存在
    pause
)
goto menu

:web_service
cls
echo 🌐 启动Web服务...
echo.
if exist "backend\enhanced_gateway.py" (
    echo 启动后端服务...
    start "EMC-Backend" python backend\enhanced_gateway.py
    timeout /t 3 >nul
    
    if exist "frontend\package.json" (
        echo 启动前端服务...
        cd frontend
        start "EMC-Frontend" cmd /k "npm start"
        cd ..
    )
    
    echo.
    echo ✅ 服务启动完成！
    echo 🌐 前端: http://localhost:3002
    echo 📊 API: http://localhost:8001/docs
) else (
    python simple-start.py
)
echo.
pause
goto menu

:demo_page
cls
echo 🎨 打开演示页面...
echo.
if exist "standalone-demo.html" (
    start "" "standalone-demo.html"
    echo ✅ 演示页面已打开
) else if exist "local-demo.html" (
    start "" "local-demo.html"
    echo ✅ 本地演示已打开
) else (
    echo ❌ 找不到演示文件
)
echo.
pause
goto menu

:docker_deploy
cls
echo 🐳 Docker部署...
echo.
echo 检查Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安装或未启动
    echo 请先安装Docker Desktop并启动
) else (
    echo ✅ Docker可用
    echo.
    echo 选择部署方式:
    echo [1] 社区版部署
    echo [2] 完整版部署
    echo.
    set /p docker_choice=请选择 (1-2): 
    
    if "!docker_choice!"=="1" (
        docker compose -f docker-compose.community.yml up -d
    ) else if "!docker_choice!"=="2" (
        cd config
        docker compose up -d
        cd ..
    )
)
echo.
pause
goto menu

:view_docs
cls
echo 📖 查看文档...
echo.
if exist "DOCKER_DEPLOYMENT.md" (
    start "" "DOCKER_DEPLOYMENT.md"
    echo ✅ 部署文档已打开
)
if exist "README_Windows.md" (
    start "" "README_Windows.md"
    echo ✅ Windows说明已打开
)
if exist "standalone-demo.html" (
    echo 💡 也可以打开 standalone-demo.html 查看系统介绍
)
echo.
pause
goto menu

:exit
cls
echo 👋 感谢使用EMC知识图谱系统！
echo.
timeout /t 2 >nul
exit

:error
echo ❌ 发生错误，请检查文件是否完整
pause
goto menu