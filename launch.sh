#!/bin/bash

# 🚀 AI Chat Assistant - Кросс-платформенный запуск
# Работает на Linux, macOS и Windows (WSL)

set -e

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Функции для вывода
print_header() {
    echo ""
    echo -e "${GREEN}======================================${NC}"
    echo -e "${GREEN}🚀 AI CHAT ASSISTANT - LAUNCHER${NC}"
    echo -e "${GREEN}======================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${CYAN}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Проверка Python
check_python() {
    print_info "Проверка Python..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 не найден!"
        print_warning "Установите Python с https://www.python.org"
        exit 1
    fi
    
    local python_version=$(python3 --version | awk '{print $2}')
    print_success "Python найден: $python_version"
}

# Проверка зависимостей
check_dependencies() {
    print_info "Проверка зависимостей..."
    
    if ! python3 -c "import flask, flask_cors" 2>/dev/null; then
        print_warning "Зависимости не установлены"
        print_info "Установка Flask и Flask-CORS..."
        
        if [ -f "requirements.txt" ]; then
            pip3 install -r requirements.txt -q
            if [ $? -eq 0 ]; then
                print_success "Зависимости установлены"
            else
                print_error "Ошибка установки зависимостей"
                exit 1
            fi
        else
            print_error "requirements.txt не найден"
            exit 1
        fi
    else
        print_success "Зависимости установлены"
    fi
}

# Проверка файлов
check_files() {
    print_info "Проверка файлов приложения..."
    
    local files=("index.html" "styles.css" "auth.js" "script.js" "server.py")
    
    for file in "${files[@]}"; do
        if [ -f "$file" ]; then
            echo -e "${GREEN}  ✅ $file${NC}"
        else
            print_error "  $file - НЕ НАЙДЕН"
            exit 1
        fi
    done
}

# Запуск сервера
start_server() {
    print_info "Запуск Flask сервера..."
    echo -e "${CYAN}URL: http://localhost:5000${NC}"
    echo -e "${CYAN}Нажмите Ctrl+C для остановки${NC}"
    echo ""
    
    python3 server.py
}

# Запуск сервера в фоне
start_server_background() {
    print_info "Запуск Flask сервера в фоне..."
    
    nohup python3 server.py > server.log 2>&1 &
    local pid=$!
    
    print_success "Сервер запущен (PID: $pid)"
    print_info "Логи: server.log"
    print_info "Остановить: kill $pid"
    
    # Подождать запуска
    echo -e "${CYAN}⏱️  Ожидание готовности сервера...${NC}"
    sleep 3
    
    # Проверить готовность
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        print_success "Сервер готов!"
    else
        print_warning "Сервер может быть не полностью готов"
    fi
}

# Открыть браузер
open_browser() {
    print_info "Открытие браузера..."
    
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:5000
    elif command -v open &> /dev/null; then
        open http://localhost:5000
    else
        print_warning "Не удалось автоматически открыть браузер"
        print_info "Откройте вручную: http://localhost:5000"
    fi
}

# Запуск тестов
run_tests() {
    print_info "Запуск тестирования API..."
    echo ""
    
    python3 test_api.py
}

# Интерактивное меню
show_menu() {
    while true; do
        echo ""
        echo -e "${GREEN}📋 МЕНЮ ЗАПУСКА:${NC}"
        echo -e "${YELLOW}   1. 🚀 Запустить сервер${NC}"
        echo -e "${YELLOW}   2. 🚀 Запустить в фоне + браузер${NC}"
        echo -e "${YELLOW}   3. 🧪 Тестирование API${NC}"
        echo -e "${YELLOW}   4. ❌ Выход${NC}"
        echo ""
        
        read -p "Выберите действие (1-4): " choice
        
        case $choice in
            1)
                start_server
                ;;
            2)
                start_server_background
                open_browser
                read -p "Нажмите Enter для возврата в меню"
                ;;
            3)
                run_tests
                ;;
            4)
                echo ""
                print_success "До свидания!"
                echo ""
                exit 0
                ;;
            *)
                print_error "Неверный выбор"
                ;;
        esac
    done
}

# Main
print_header

# Проверки
check_python
check_dependencies
check_files

# Меню
show_menu
