@echo off
REM 🚀 AI Chat - Автозапуск для Windows
REM Этот файл запускает всё необходимое одной кнопкой

setlocal enabledelayedexpansion
chcp 65001 >nul

echo.
echo ================================================================
echo        🚀 AI CHAT ASSISTANT - АВТОМАТИЧЕСКИЙ ЗАПУСК
echo ================================================================
echo.

REM Проверить что мы в правильной папке
if not exist server.py (
    echo ❌ Ошибка: server.py не найден!
    echo Пожалуйста запустите файл из папки приложения
    pause
    exit /b 1
)

REM Проверить Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не найден!
    echo Пожалуйста установите Python с https://python.org
    pause
    exit /b 1
)

echo ✅ Python найден

REM Проверить зависимости
echo.
echo 🔍 Проверка зависимостей...
python -c "import flask, flask_cors" >nul 2>&1
if errorlevel 1 (
    echo ❌ Зависимости не установлены
    echo 📦 Установка Flask и Flask-CORS...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Ошибка установки зависимостей
        pause
        exit /b 1
    )
) else (
    echo ✅ Зависимости установлены
)

REM Проверить наличие ключей файлов
echo.
echo 🔍 Проверка файлов приложения...
for %%F in (index.html styles.css auth.js script.js) do (
    if not exist %%F (
        echo ❌ Файл %%F не найден!
        pause
        exit /b 1
    )
)
echo ✅ Все файлы на месте

REM Запустить Python launcher
echo.
echo 🚀 Запуск приложения...
echo.
python launch.py

pause
exit /b 0
