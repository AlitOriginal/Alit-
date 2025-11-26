"""
Client script to connect to Alit Chat Server
Используйте этот скрипт для подключения к удаленному серверу
"""

import requests
import json
import sys
from datetime import datetime

class AitClientConnector:
    def __init__(self, server_url, username, password):
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.client_id = None
        self.session_id = None
        
    def login(self):
        """Авторизоваться на сервере"""
        try:
            response = self.session.post(
                f'{self.server_url}/api/auth/login',
                json={'username': self.username, 'password': self.password}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Успешный вход: {data['user']['username']}")
                return True
            else:
                print(f"❌ Ошибка входа: {response.json()['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка подключения: {str(e)}")
            return False
    
    def register(self, email):
        """Зарегистрировать нового пользователя"""
        try:
            response = self.session.post(
                f'{self.server_url}/api/auth/register',
                json={
                    'username': self.username,
                    'password': self.password,
                    'email': email
                }
            )
            
            if response.status_code == 201:
                print(f"✅ Пользователь зарегистрирован: {self.username}")
                return True
            else:
                print(f"❌ Ошибка регистрации: {response.json()['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return False
    
    def connect_client(self, device_info=None):
        """Подключить клиент"""
        try:
            response = self.session.post(
                f'{self.server_url}/api/clients/connect',
                json={
                    'device_info': device_info or {'os': 'Windows', 'app': 'Alit Client'}
                }
            )
            
            if response.status_code == 201:
                data = response.json()['session']
                self.client_id = data['client_id']
                self.session_id = data['session_id']
                print(f"✅ Клиент подключен!")
                print(f"   Client ID: {self.client_id}")
                print(f"   IP адрес: {data['ip_address']}")
                return True
            else:
                print(f"❌ Ошибка подключения: {response.json()['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return False
    
    def send_heartbeat(self):
        """Отправить heartbeat"""
        if not self.client_id:
            return False
            
        try:
            response = self.session.post(
                f'{self.server_url}/api/clients/heartbeat',
                json={'client_id': self.client_id}
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ Heartbeat ошибка: {str(e)}")
            return False
    
    def disconnect_client(self):
        """Отключить клиент"""
        if not self.client_id:
            return False
            
        try:
            response = self.session.post(
                f'{self.server_url}/api/clients/disconnect',
                json={'client_id': self.client_id}
            )
            
            if response.status_code == 200:
                print(f"✅ Клиент отключен")
                return True
            else:
                print(f"❌ Ошибка отключения: {response.json()['error']}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return False
    
    def get_server_info(self):
        """Получить информацию о сервере"""
        try:
            response = self.session.get(f'{self.server_url}/api/health')
            
            if response.status_code == 200:
                data = response.json()
                print("📊 Информация о сервере:")
                print(f"   Статус: {data['status']}")
                print(f"   Пользователей: {data['users_count']}")
                print(f"   Сообщений: {data['messages_count']}")
                print(f"   Активных клиентов: {data['active_clients']}")
                print(f"   Активных сессий: {data['active_sessions']}")
                return True
            else:
                print("❌ Ошибка получения информации")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            return False


def main():
    print("=" * 70)
    print("Alit Chat Client Connector")
    print("=" * 70)
    
    # Получить параметры
    server_url = input("🖥️  Введите адрес сервера (например http://192.168.1.100:5000): ").strip()
    username = input("👤 Введите имя пользователя: ").strip()
    
    # Попытка входа
    password = input("🔐 Введите пароль: ").strip()
    
    connector = AitClientConnector(server_url, username, password)
    
    # Пробуем войти, если не получается - регистрируемся
    print("\n🔄 Попытка входа...")
    if not connector.login():
        print("\n📝 Регистрация нового пользователя...")
        email = input("📧 Введите email: ").strip()
        if not connector.register(email):
            return
        
        if not connector.login():
            print("❌ Не удалось войти после регистрации")
            return
    
    # Подключить клиент
    print("\n🔗 Подключение клиента...")
    if not connector.connect_client():
        return
    
    # Получить информацию о сервере
    print()
    connector.get_server_info()
    
    # Меню
    print("\n" + "=" * 70)
    print("✅ Успешно подключены! Что дальше?")
    print("=" * 70)
    print("1. Отправить heartbeat")
    print("2. Получить информацию о сервере")
    print("3. Отключиться")
    print("0. Выход")
    print("=" * 70)
    
    while True:
        choice = input("\n📌 Выберите действие (0-3): ").strip()
        
        if choice == '0':
            print("До свидания!")
            break
        elif choice == '1':
            if connector.send_heartbeat():
                print("✅ Heartbeat отправлен")
            else:
                print("❌ Ошибка отправки heartbeat")
        elif choice == '2':
            connector.get_server_info()
        elif choice == '3':
            connector.disconnect_client()
            break
        else:
            print("❌ Неверный выбор")


if __name__ == '__main__':
    main()
