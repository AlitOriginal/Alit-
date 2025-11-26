#!/usr/bin/env python3
"""
🚀 AI Chat Assistant - АВТОМАТИЧЕСКИЙ ЗАПУСК
Этот скрипт запустит всё необходимое одной командой
"""

import subprocess
import sys
import os
import time
import webbrowser
import platform
import json
from pathlib import Path

class AppLauncher:
    def __init__(self):
        self.app_dir = Path(__file__).parent
        self.os_type = platform.system()
        
    def print_header(self):
        print("\n" + "="*70)
        print("🚀 AI CHAT ASSISTANT - АВТОМАТИЧЕСКИЙ ЗАПУСК")
        print("="*70 + "\n")
    
    def check_dependencies(self):
        """Проверить установлены ли зависимости"""
        print("🔍 Проверка зависимостей...")
        
        try:
            import flask
            import flask_cors
            print("✅ Flask установлен")
            return True
        except ImportError:
            print("❌ Flask не установлен")
            print("📦 Попытка установить зависимости...")
            return self.install_dependencies()
    
    def install_dependencies(self):
        """Установить зависимости"""
        try:
            print("📦 Установка зависимостей Python...")
            req_file = self.app_dir / 'requirements.txt'
            if req_file.exists():
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', str(req_file)],
                    check=True
                )
                print("✅ Зависимости установлены\n")
                return True
            else:
                print("❌ requirements.txt не найден")
                return False
        except Exception as e:
            print(f"❌ Ошибка установки: {e}")
            return False
    
    def check_api_key(self):
        """Проверить наличие API ключа"""
        script_file = self.app_dir / 'script.js'
        if script_file.exists():
            content = script_file.read_text(encoding='utf-8')
            if 'sk-proj-' in content and 'sk-proj-anaFLtXFzeAsxMuDc' not in content:
                print("✅ API ключ установлен\n")
                return True
            else:
                print("⚠️  API ключ не установлен или значение по умолчанию")
                print("📝 Пожалуйста добавьте ваш API ключ OpenAI в script.js\n")
                return False
        return False
    
    def start_server(self):
        """Запустить Flask сервер"""
        print("🚀 Запуск Flask сервера...")
        print("   URL: http://localhost:5000")
        print("   Нажмите Ctrl+C для остановки\n")
        
        try:
            os.chdir(self.app_dir)
            subprocess.run([sys.executable, 'server.py'])
        except KeyboardInterrupt:
            print("\n\n⏹️  Сервер остановлен")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Ошибка запуска сервера: {e}")
            sys.exit(1)
    
    def run_interactive_menu(self):
        """Интерактивное меню запуска"""
        while True:
            print("\n📋 МЕНЮ ЗАПУСКА:")
            print("   1. 🚀 Запустить сервер")
            print("   2. 🧪 Запустить тестирование API")
            print("   3. ⚙️  Запустить менеджер сервера")
            print("   4. 🌐 Открыть в браузере")
            print("   5. ❌ Выход\n")
            
            choice = input("Выберите действие (1-5): ").strip()
            
            if choice == '1':
                self.start_server()
            elif choice == '2':
                self.run_test_api()
            elif choice == '3':
                self.run_manager()
            elif choice == '4':
                self.open_browser()
            elif choice == '5':
                print("\n👋 До свидания!\n")
                sys.exit(0)
            else:
                print("❌ Неверный выбор")
    
    def run_test_api(self):
        """Запустить тестирование API"""
        print("\n🧪 Запуск тестирования API...")
        try:
            os.chdir(self.app_dir)
            subprocess.run([sys.executable, 'test_api.py'])
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def run_manager(self):
        """Запустить менеджер сервера"""
        print("\n⚙️  Запуск менеджера сервера...")
        try:
            os.chdir(self.app_dir)
            subprocess.run([sys.executable, 'manage_server.py'])
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    def open_browser(self):
        """Открыть браузер"""
        print("\n🌐 Открытие браузера...")
        webbrowser.open('http://localhost:5000')
        print("✅ Браузер открыт на http://localhost:5000")
    
    def run(self, auto_start=False):
        """Главный метод запуска"""
        self.print_header()
        
        # Проверить зависимости
        if not self.check_dependencies():
            print("❌ Не удалось установить зависимости")
            print("Пожалуйста установите вручную:")
            print("  pip install -r requirements.txt")
            sys.exit(1)
        
        # Проверить API ключ
        self.check_api_key()
        
        if auto_start:
            # Автоматический запуск
            print("⏱️  Сервер запустится через 2 секунды...\n")
            time.sleep(2)
            self.start_server()
        else:
            # Интерактивное меню
            self.run_interactive_menu()

if __name__ == '__main__':
    launcher = AppLauncher()
    
    # Запустить с опциями
    auto_start = '--auto' in sys.argv or '-a' in sys.argv
    
    try:
        launcher.run(auto_start=auto_start)
    except KeyboardInterrupt:
        print("\n\n👋 Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)
