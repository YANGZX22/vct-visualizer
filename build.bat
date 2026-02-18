@echo off
chcp 65001 >nul
echo ========================================
echo   VCT Display Demo 编译工具
echo ========================================
echo.

:: 检查虚拟环境
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 未找到虚拟环境，请先创建 .venv
    pause
    exit /b 1
)

:: 检查PyInstaller
.venv\Scripts\pip.exe show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [提示] 正在安装 PyInstaller...
    .venv\Scripts\pip.exe install pyinstaller
)

:: 检查icon.ico
if exist "icon.ico" del /f "icon.ico"
echo [提示] 正在生成 icon.ico...
.venv\Scripts\python.exe -c "from PIL import Image; img = Image.open('icon.jpg'); img.save('icon.ico', format='ICO', sizes=[(256,256),(128,128),(64,64),(48,48),(32,32),(16,16)])"

:: 清理旧文件
echo [1/3] 清理旧的编译文件...
if exist "dist\VCT_Display.exe" del /f "dist\VCT_Display.exe"
if exist "build" rmdir /s /q "build"
if exist "__pycache__" rmdir /s /q "__pycache__"
if exist "*.spec" del /f "*.spec"

:: 编译 (添加 --clean 参数清理缓存)
echo [2/3] 正在编译，请稍候...
.venv\Scripts\pyinstaller.exe --clean --onefile --windowed --icon=icon.ico --name="VCT_Display" --add-data="assets;assets" --add-data="icon.jpg;." --add-data="LICENSE;." main.py

:: 检查结果
echo.
if exist "dist\VCT_Display.exe" (
    echo ========================================
    echo   编译成功！
    echo   输出文件: dist\VCT_Display.exe
    echo ========================================
) else (
    echo [错误] 编译失败，请检查错误信息
)

echo.
pause
