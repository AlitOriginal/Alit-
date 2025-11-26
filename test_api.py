"""
API Testing Script - проверка функциональности сервера
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:5000/api"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.username = "test_user"
        self.password = "test_password_123"
        self.email = "test@example.com"
        self.user_id = None

    def print_header(self, text):
        print(f"\n{'='*50}")
        print(f"  {text}")
        print(f"{'='*50}\n")

    def test_health(self):
        """Проверка статуса сервера"""
        self.print_header("🏥 HEALTH CHECK")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Сервер работает")
                print(f"   Статус: {data['status']}")
                print(f"   Пользователей: {data['users_count']}")
                print(f"   Сообщений: {data['messages_count']}")
            else:
                print(f"❌ Ошибка: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")

    def test_register(self):
        """Регистрация пользователя"""
        self.print_header("👤 РЕГИСТРАЦИЯ")
        try:
            data = {
                "username": self.username,
                "email": self.email,
                "password": self.password
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=data)
            
            if response.status_code == 201:
                result = response.json()
                self.user_id = result['user']['id']
                print(f"✅ Пользователь зарегистрирован")
                print(f"   ID: {self.user_id}")
                print(f"   Username: {self.username}")
            elif response.status_code == 400:
                print(f"⚠️  Пользователь уже существует (используем существующего)")
            else:
                print(f"❌ Ошибка: {response.json()}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def test_login(self):
        """Вход пользователя"""
        self.print_header("🔐 ВХОД")
        try:
            data = {
                "username": self.username,
                "password": self.password
            }
            response = self.session.post(f"{BASE_URL}/auth/login", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Вход выполнен успешно")
                print(f"   Username: {result['user']['username']}")
                print(f"   Email: {result['user']['email']}")
            else:
                print(f"❌ Ошибка: {response.json()}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def test_get_user(self):
        """Получить текущего пользователя"""
        self.print_header("📋 ПОЛУЧИТЬ ПРОФИЛЬ")
        try:
            response = self.session.get(f"{BASE_URL}/auth/user")
            
            if response.status_code == 200:
                user = response.json()
                print(f"✅ Профиль получен")
                print(f"   Username: {user['username']}")
                print(f"   Email: {user['email']}")
            else:
                print(f"❌ Ошибка: {response.json()}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def test_send_message(self, content):
        """Отправить сообщение"""
        self.print_header("💬 ОТПРАВИТЬ СООБЩЕНИЕ")
        try:
            data = {"content": content}
            response = self.session.post(f"{BASE_URL}/chat/messages", json=data)
            
            if response.status_code == 201:
                msg = response.json()
                print(f"✅ Сообщение отправлено")
                print(f"   ID: {msg['id']}")
                print(f"   Content: {msg['content']}")
                print(f"   Timestamp: {msg['timestamp']}")
                return msg['id']
            else:
                print(f"❌ Ошибка: {response.json()}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def test_get_messages(self, limit=10):
        """Получить сообщения"""
        self.print_header("📨 ПОЛУЧИТЬ СООБЩЕНИЯ")
        try:
            response = self.session.get(f"{BASE_URL}/chat/messages?limit={limit}")
            
            if response.status_code == 200:
                messages = response.json()
                print(f"✅ Получено {len(messages)} сообщений")
                for i, msg in enumerate(messages[-3:], 1):
                    print(f"\n   Сообщение {i}:")
                    print(f"     Username: {msg['username']}")
                    print(f"     Content: {msg['content'][:50]}...")
            else:
                print(f"❌ Ошибка: {response.json()}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def test_delete_message(self, message_id):
        """Удалить сообщение"""
        self.print_header("🗑️  УДАЛИТЬ СООБЩЕНИЕ")
        try:
            response = self.session.delete(f"{BASE_URL}/chat/messages/{message_id}")
            
            if response.status_code == 200:
                print(f"✅ Сообщение удалено")
            else:
                print(f"❌ Ошибка: {response.json()}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def test_logout(self):
        """Выход"""
        self.print_header("🚪 ВЫХОД")
        try:
            response = self.session.post(f"{BASE_URL}/auth/logout")
            
            if response.status_code == 200:
                print(f"✅ Вы вышли")
            else:
                print(f"❌ Ошибка: {response.json()}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

    def run_all_tests(self):
        """Запустить все тесты"""
        print("\n" + "="*50)
        print("  🧪 ТЕСТИРОВАНИЕ API")
        print("="*50)
        
        # Проверка сервера
        self.test_health()
        input("\n[Enter для продолжения]")
        
        # Регистрация и вход
        self.test_register()
        input("\n[Enter для продолжения]")
        
        self.test_login()
        input("\n[Enter для продолжения]")
        
        # Получить профиль
        self.test_get_user()
        input("\n[Enter для продолжения]")
        
        # Отправить сообщение
        msg_id = self.test_send_message("🧪 Тестовое сообщение из API tester")
        input("\n[Enter для продолжения]")
        
        # Получить сообщения
        self.test_get_messages()
        input("\n[Enter для продолжения]")
        
        # Удалить сообщение
        if msg_id:
            self.test_delete_message(msg_id)
            input("\n[Enter для продолжения]")
        
        # Выход
        self.test_logout()
        
        print("\n" + "="*50)
        print("  ✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("="*50 + "\n")

if __name__ == "__main__":
    print("\n🔄 Убедитесь что сервер запущен на http://localhost:5000")
    input("Нажмите Enter для начала тестирования...")
    
    tester = APITester()
    tester.run_all_tests()
