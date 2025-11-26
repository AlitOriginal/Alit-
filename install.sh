#!/bin/bash

echo "========================================================"
echo ""
echo "  🚀 AI CHAT ASSISTANT - УСТАНОВКА ЗАВИСИМОСТЕЙ"
echo ""
echo "========================================================"
echo ""

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не установлен!"
    echo "Пожалуйста установите Python с https://www.python.org/"
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"
echo ""
echo "📦 Установка зависимостей..."
echo ""

pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Зависимости успешно установлены!"
    echo ""
    echo "Для запуска используйте:"
    echo "  python3 manage_server.py"
else
    echo ""
    echo "❌ Ошибка при установке зависимостей"
    exit 1
fi
