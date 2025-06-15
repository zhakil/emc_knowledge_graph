@echo off
echo =================================================
echo EMC知识图谱 - Windows桌面客户端构建脚本
echo =================================================
echo.

echo [1/5] 检查环境...
call npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ NPM未安装，请先安装Node.js
    pause
    exit /b 1
)
echo ✅ 开发环境检查通过

echo.
echo [2/5] 清理并安装依赖...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
call npm cache clean --force
call npm install --legacy-peer-deps
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

echo.
echo [3/5] 构建React应用...
call npm run build
if errorlevel 1 (
    echo ❌ React应用构建失败
    pause
    exit /b 1
)
echo ✅ React应用构建完成

echo.
echo [4/5] 构建Windows安装包...
call npm run dist
if errorlevel 1 (
    echo ❌ Windows安装包构建失败
    pause
    exit /b 1
)
echo ✅ Windows安装包构建完成

echo.
echo [5/5] 构建完成
echo =================================================
echo 📦 构建输出文件:
echo    📁 dist/EMC知识图谱系统-1.0.0-x64.exe
echo    📁 dist/EMC知识图谱系统-1.0.0-portable.exe
echo    📄 dist/latest.yml
echo =================================================
echo.
echo ✅ 构建成功完成！
echo 你现在可以运行安装程序来安装桌面客户端
echo.
pause