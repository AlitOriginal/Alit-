#!/usr/bin/env python3
import os
import sys
import subprocess
import json
import time
from pathlib import Path
import platform

class ServerManager:
    def __init__(self):
        self.server_process = None
        self.server_path = Path(__file__).parent / 'server.py'
        self.is_running = False
        self.os_type = platform.system()

    def print_header(self):
        print("\n" + "="*60)
        print("🚀 AI CHAT SERVER MANAGER")
        print("="*60 + "\n")

    def print_menu(self):
        print("📋 МЕНЮ УПРАВЛЕНИЯ:")
        print(f"  1. {'▶️  Запустить' if not self.is_running else '🛑 Сервер уже запущен'}")
        print(f"  2. {'⏹️  Остановить' if self.is_running else '❌ Сервер не запущен'}")
        print("  3. ℹ️  Статус сервера")
        print("  4. 📁 Просмотр данных пользователей")
        print("  5. 📨 Просмотр сообщений")
        print("  6. 🗑️  Очистить данные")
        print("  7. 🌐 Открыть приложение в браузере")
        print("  8. ❌ Выход")
        print()

    def start_server(self):
        if self.is_running:
            print("⚠️  Сервер уже запущен!")
            return

        print("🚀 Запуск сервера...")
        try:
            if self.os_type == 'Windows':
                self.server_process = subprocess.Popen(
                    [sys.executable, str(self.server_path)],
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                self.server_process = subprocess.Popen(
                    [sys.executable, str(self.server_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            
            self.is_running = True
            print("✅ Сервер успешно запущен!")
            print("📍 URL: http://localhost:5000")
            print("⏱️  Подождите 2 секунды для полной инициализации...")
            time.sleep(2)

        except Exception as e:
            print(f"❌ Ошибка при запуске сервера: {e}")

    def stop_server(self):
        if not self.is_running:
            print("⚠️  Сервер не запущен!")
            return

        print("⏹️  Остановка сервера...")
        try:
            if self.server_process:
                if self.os_type == 'Windows':
                    self.server_process.terminate()
                else:
                    self.server_process.terminate()
                    self.server_process.wait(timeout=5)
            
            self.is_running = False
            self.server_process = None
            print("✅ Сервер успешно остановлен!")

        except Exception as e:
            print(f"❌ Ошибка при остановке сервера: {e}")

    def check_status(self):
        print("\n📊 СТАТУС СЕРВЕРА:")
        print(f"  Статус: {'🟢 Работает' if self.is_running else '🔴 Не работает'}")
        print(f"  PID: {self.server_process.pid if self.is_running and self.server_process else 'N/A'}")
        print(f"  URL: http://localhost:5000")
        print(f"  OS: {self.os_type}")
        
        # Check data files
        data_dir = Path(__file__).parent / 'data'
        if data_dir.exists():
            users_file = data_dir / 'users.json'
            messages_file = data_dir / 'messages.json'
            
            users_count = len(json.load(open(users_file))) if users_file.exists() else 0
            messages_count = len(json.load(open(messages_file))) if messages_file.exists() else 0
            
            print(f"\n  📊 Статистика:")
            print(f"    - Пользователей: {users_count}")
            print(f"    - Сообщений: {messages_count}")
        print()

    def view_users(self):
        data_dir = Path(__file__).parent / 'data'
        users_file = data_dir / 'users.json'
        
        if not users_file.exists():
            print("❌ Файл пользователей не найден!")
            return
        
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            print("\n👥 ПОЛЬЗОВАТЕЛИ:")
            if not users:
                print("  Нет пользователей")
            else:
                for username, user_data in users.items():
                    print(f"\n  👤 {username}")
                    print(f"    Email: {user_data['email']}")
                    print(f"    ID: {user_data['id']}")
                    print(f"    Создан: {user_data['created_at']}")
            print()
        
        except Exception as e:
            print(f"❌ Ошибка при чтении пользователей: {e}")

    def view_messages(self):
        data_dir = Path(__file__).parent / 'data'
        messages_file = data_dir / 'messages.json'
        
        if not messages_file.exists():
            print("❌ Файл сообщений не найден!")
            return
        
        try:
            with open(messages_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
            
            print("\n💬 СООБЩЕНИЯ (последние 10):")
            if not messages:
                print("  Нет сообщений")
            else:
                for msg in messages[-10:]:
                    print(f"\n  👤 {msg['username']}: {msg['content'][:50]}...")
                    print(f"    Время: {msg['timestamp']}")
            print()
        
        except Exception as e:
            print(f"❌ Ошибка при чтении сообщений: {e}")

    def clear_data(self):
        confirm = input("⚠️  Вы уверены? Все данные будут удалены. (да/нет): ").strip().lower()
        if confirm != 'да':
            print("❌ Отменено")
            return
        
        data_dir = Path(__file__).parent / 'data'
        try:
            users_file = data_dir / 'users.json'
            messages_file = data_dir / 'messages.json'
            
            if users_file.exists():
                users_file.write_text('{}')
                print("✅ Пользователи очищены")
            
            if messages_file.exists():
                messages_file.write_text('[]')
                print("✅ Сообщения очищены")
            
            print("✅ Данные успешно очищены!")
        
        except Exception as e:
            print(f"❌ Ошибка при очистке данных: {e}")

    def open_browser(self):
        import webbrowser
        print("🌐 Открытие приложения в браузере...")
        webbrowser.open('http://localhost:5000')

    def run(self):
        self.print_header()
        
        while True:
            self.print_menu()
            choice = input("Выберите опцию (1-8): ").strip()
            
            if choice == '1':
                self.start_server()
            elif choice == '2':
                self.stop_server()
            elif choice == '3':
                self.check_status()
            elif choice == '4':
                self.view_users()
            elif choice == '5':
                self.view_messages()
            elif choice == '6':
                self.clear_data()
            elif choice == '7':
                self.open_browser()
            elif choice == '8':
                if self.is_running:
                    print("🛑 Остановка сервера перед выходом...")
                    self.stop_server()
                print("👋 До свидания!")
                sys.exit(0)
            else:
                print("❌ Неверный выбор. Попробуйте снова.\n")

if __name__ == '__main__':
    manager = ServerManager()
    
    # Обработка Ctrl+C
    try:
        manager.run()
    except KeyboardInterrupt:
        print("\n\n🛑 Прервано пользователем")
        if manager.is_running:
            print("Остановка сервера...")
            manager.stop_server()
        sys.exit(0)
