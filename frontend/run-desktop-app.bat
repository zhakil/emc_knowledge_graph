@echo off
echo =================================================
echo EMC知识图谱 - Windows桌面客户端启动脚本
echo =================================================
echo.

echo [1/4] 检查依赖...
call npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ NPM未安装，请先安装Node.js
    pause
    exit /b 1
)
echo ✅ NPM已安装

echo.
echo [2/4] 安装依赖包...
call npm install --legacy-peer-deps
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

echo.
echo [3/4] 构建React应用...
call npm run build
if errorlevel 1 (
    echo ❌ React应用构建失败
    pause
    exit /b 1
)
echo ✅ React应用构建完成

echo.
echo [4/4] 启动桌面应用...
echo 正在启动EMC知识图谱桌面客户端...
call npm run electron
if errorlevel 1 (
    echo ❌ 桌面应用启动失败
    pause
    exit /b 1
)

echo.
echo ✅ 应用程序已启动
pause