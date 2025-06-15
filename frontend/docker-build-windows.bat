@echo off
echo =====================================================
echo EMC知识图谱 Windows桌面客户端 Docker构建
echo =====================================================
echo.

echo [1/3] 检查Docker环境...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker未安装或未启动
    echo 请确保Docker Desktop已安装并运行
    pause
    exit /b 1
)
echo ✅ Docker环境正常

echo.
echo [2/3] 构建Docker镜像...
docker build -f Dockerfile.desktop -t emc-knowledge-graph-builder .
if errorlevel 1 (
    echo ❌ Docker镜像构建失败
    pause
    exit /b 1
)
echo ✅ Docker镜像构建完成

echo.
echo [3/3] 在Docker容器中构建Windows桌面客户端...
docker run --rm -v "%cd%\dist:/app/dist" emc-knowledge-graph-builder
if errorlevel 1 (
    echo ❌ 容器构建失败
    pause
    exit /b 1
)

echo.
echo ==============================================
echo 🎉 构建完成！
echo ==============================================
echo 📁 构建文件位置: %cd%\dist\
echo.
echo 生成的安装包文件:
dir dist\*.exe 2>nul || echo   (构建完成后将显示exe文件)
echo.
echo 📦 EMC知识图谱系统-1.0.0-x64.exe - Windows安装程序
echo 📦 EMC知识图谱系统-1.0.0-portable.exe - 便携版
echo 📄 latest.yml - 自动更新配置
echo.
echo ✅ 现在可以运行安装程序来安装桌面客户端！
pause