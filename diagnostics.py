#!/usr/bin/env python3
"""
🔍 ДИАГНОСТИКА СИСТЕМЫ
Проверяет готовность приложения к запуску
"""

import os
import sys
import subprocess
from pathlib import Path

class SystemDiagnostics:
    def __init__(self):
        self.app_dir = Path(__file__).parent
        self.checks_passed = 0
        self.checks_failed = 0
        
    def print_header(self):
        print("\n" + "=" * 70)
        print("🔍 ДИАГНОСТИКА СИСТЕМЫ AI CHAT ASSISTANT")
        print("=" * 70 + "\n")
    
    def print_check(self, name, passed, message=""):
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if message:
            print(f"   └─ {message}")
        
        if passed:
            self.checks_passed += 1
        else:
            self.checks_failed += 1
    
    def check_python(self):
        """Проверить Python"""
        print("📦 Проверка Python...\n")
        
        try:
            version = subprocess.check_output(
                [sys.executable, '--version'],
                text=True
            ).strip()
            self.print_check("Python установлен", True, f"Версия: {version}")
            return True
        except:
            self.print_check("Python установлен", False, "Python не найден")
            return False
    
    def check_dependencies(self):
        """Проверить зависимости"""
        print("\n🔧 Проверка зависимостей...\n")
        
        try:
            import flask
            self.print_check("Flask установлен", True, f"Версия: {flask.__version__}")
        except:
            self.print_check("Flask установлен", False, "Установите: pip install flask")
        
        try:
            import flask_cors
            self.print_check("Flask-CORS установлен", True, "✅")
        except:
            self.print_check("Flask-CORS установлен", False, "Установите: pip install flask-cors")
        
        try:
            from werkzeug.security import generate_password_hash
            self.print_check("Werkzeug установлен", True, "✅")
        except:
            self.print_check("Werkzeug установлен", False, "Обычно включён в Flask")
    
    def check_files(self):
        """Проверить основные файлы"""
        print("\n📂 Проверка файлов приложения...\n")
        
        required_files = {
            "index.html": "Главная страница",
            "styles.css": "Стили CSS",
            "auth.js": "Система аутентификации",
            "script.js": "Логика приложения",
            "server.py": "Flask сервер",
            "requirements.txt": "Зависимости Python",
        }
        
        for filename, description in required_files.items():
            path = self.app_dir / filename
            exists = path.exists()
            self.print_check(f"{filename}", exists, description)
    
    def check_data_dir(self):
        """Проверить папку данных"""
        print("\n💾 Проверка папки данных...\n")
        
        data_dir = self.app_dir / "data"
        exists = data_dir.exists()
        self.print_check("Папка data существует", exists)
        
        if exists:
            users_file = data_dir / "users.json"
            messages_file = data_dir / "messages.json"
            
            if users_file.exists():
                size = users_file.stat().st_size
                self.print_check("users.json", True, f"Размер: {size} байт")
            else:
                self.print_check("users.json", False, "Будет создан при запуске")
            
            if messages_file.exists():
                size = messages_file.stat().st_size
                self.print_check("messages.json", True, f"Размер: {size} байт")
            else:
                self.print_check("messages.json", False, "Будет создан при запуске")
    
    def check_scripts(self):
        """Проверить скрипты запуска"""
        print("\n🚀 Проверка скриптов запуска...\n")
        
        scripts = {
            "launch.py": "Python меню",
            "launch.ps1": "PowerShell меню",
            "RUN.bat": "Главный файл",
            "start.bat": "Менеджер сервера",
        }
        
        for script, description in scripts.items():
            path = self.app_dir / script
            exists = path.exists()
            self.print_check(script, exists, description)
    
    def check_api_key(self):
        """Проверить API ключ"""
        print("\n🔑 Проверка API ключа...\n")
        
        script_file = self.app_dir / "script.js"
        if script_file.exists():
            content = script_file.read_text(encoding='utf-8')
            
            if "sk-proj-" in content:
                # Проверить, не стоит ли дефолтный ключ
                if "sk-proj-anaFLtXFzeAsxMuDc" in content:
                    self.print_check(
                        "API ключ OpenAI",
                        False,
                        "Нужен действительный ключ с https://platform.openai.com/api-keys"
                    )
                else:
                    self.print_check(
                        "API ключ OpenAI",
                        True,
                        "Ключ установлен (убедитесь что он действительный)"
                    )
            else:
                self.print_check(
                    "API ключ OpenAI",
                    False,
                    "Ключ не найден, добавьте в script.js"
                )
    
    def check_documentation(self):
        """Проверить документацию"""
        print("\n📚 Проверка документации...\n")
        
        docs = {
            "README.md": "Основная документация",
            "ЗАПУСК.md": "Инструкция на русском",
            "ВСЕ_СПОСОБЫ_ЗАПУСКА.txt": "Варианты запуска",
            "ФИНАЛЬНОЕ_РЕЗЮМЕ.txt": "Резюме проекта",
        }
        
        for doc, description in docs.items():
            path = self.app_dir / doc
            exists = path.exists()
            self.print_check(doc, exists, description)
    
    def print_summary(self):
        """Вывести итоги"""
        print("\n" + "=" * 70)
        print("📊 ИТОГИ ДИАГНОСТИКИ")
        print("=" * 70 + "\n")
        
        total = self.checks_passed + self.checks_failed
        percentage = (self.checks_passed / total * 100) if total > 0 else 0
        
        print(f"✅ Прошли проверки: {self.checks_passed}")
        print(f"❌ Не прошли проверки: {self.checks_failed}")
        print(f"📊 Успешность: {percentage:.1f}%")
        
        if self.checks_failed == 0:
            print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ! Приложение готово!")
            print("\n🚀 Запустите RUN.bat для начала работы\n")
            return True
        else:
            print(f"\n⚠️  Есть {self.checks_failed} проблем(ы)")
            print("Пожалуйста решите их перед запуском\n")
            return False
    
    def run(self):
        """Главный метод"""
        self.print_header()
        
        self.check_python()
        self.check_dependencies()
        self.check_files()
        self.check_data_dir()
        self.check_scripts()
        self.check_api_key()
        self.check_documentation()
        
        success = self.print_summary()
        
        return 0 if success else 1

if __name__ == "__main__":
    diag = SystemDiagnostics()
    exit_code = diag.run()
    
    input("Нажмите Enter для выхода...")
    sys.exit(exit_code)
