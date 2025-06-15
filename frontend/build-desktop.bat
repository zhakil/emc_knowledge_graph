@echo off
echo 🚀 构建EMC知识图谱Windows桌面应用程序...

REM 检查Node.js
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装，请先安装Node.js
    pause
    exit /b 1
)

REM 检查npm
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ npm未安装，请先安装npm
    pause
    exit /b 1
)

REM 清理旧的构建文件
echo 🧹 清理旧的构建文件...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

REM 安装依赖
echo 📦 安装依赖包...
call npm install
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

REM 构建React应用
echo 🔨 构建React前端应用...
call npm run build
if %errorlevel% neq 0 (
    echo ❌ React应用构建失败
    pause
    exit /b 1
)

REM 构建Electron应用
echo 🖥️ 构建Electron桌面应用...
call npm run dist
if %errorlevel% neq 0 (
    echo ❌ Electron应用构建失败
    pause
    exit /b 1
)

REM 检查输出
if exist dist (
    echo ✅ 构建成功！
    echo.
    echo 📁 输出文件位置: .\dist\
    echo 🔍 生成的文件:
    dir /b dist\*.exe 2>nul && (
        for %%f in (dist\*.exe) do echo   📦 %%f
    )
    echo.
    echo 🎉 EMC知识图谱桌面应用程序已生成完成！
    echo 💾 安装包: EMC知识图谱系统-1.0.0-x64.exe
    echo 🎒 便携版: EMC知识图谱系统-1.0.0-portable.exe
    echo.
    echo 📋 使用说明:
    echo 1. 双击.exe文件安装或运行
    echo 2. 支持系统托盘最小化
    echo 3. 快捷键 Ctrl+Shift+E 显示/隐藏窗口
    echo 4. 内置完整API服务器，无需额外配置
    echo.
    echo 📚 详细文档: docs\WINDOWS_APP_GUIDE.md
    echo.
    echo 按任意键打开输出文件夹...
    pause >nul
    explorer dist
) else (
    echo ❌ 构建失败，请检查错误信息
    pause
    exit /b 1
)