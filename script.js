// Chat Application
class ChatApplication {
    constructor() {
        // Получить базовый URL сервера (может быть localhost или IP адрес)
        const protocol = window.location.protocol;
        const host = window.location.hostname;
        const baseUrl = `${protocol}//${host}:5000`;
        
        // Локальная ИИ (Ollama) - проксируется через основной сервер
        this.ollamaUrl = `${baseUrl}/api/ollama/chat`;
        this.ollamaModel = 'mistral';
        this.serverUrl = `${baseUrl}/api`;
        
        // Задержка между запросами (в миллисекундах)
        this.requestDelay = 1000; // 1 секунда между запросами
        this.lastRequestTime = 0;
        
        this.currentChatId = 1;
        this.conversationHistory = [];
        this.chats = {
            1: {
                id: 1,
                title: 'Первый разговор',
                messages: []
            }
        };
        
        this.currentView = 'ai-chat';
        this.globalMessages = [];
        this.globalChatPolling = null;

        this.initializeElements();
        this.attachEventListeners();
    }

    initializeElements() {
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.chatMessages = document.getElementById('chatMessages');
        
        this.globalMessageInput = document.getElementById('globalMessageInput');
        this.globalSendBtn = document.getElementById('globalSendBtn');
        this.globalChatMessages = document.getElementById('globalChatMessages');

        // Mobile elements
        this.mobileMenuToggle = document.getElementById('mobileMenuToggle');
        this.mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
        this.sidebar = document.getElementById('sidebar');
        this.mobileNewChatBtn = document.getElementById('mobileNewChatBtn');
        this.mobileBottomNav = document.getElementById('mobileBottomNav');
    }

    getAuthHeaders() {
        // Get Authorization headers if token is available
        const headers = { 'Content-Type': 'application/json' };
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        if (user && user.token) {
            headers['Authorization'] = `Bearer ${user.token}`;
        }
        return headers;
    }

    hasValidToken() {
        // Check if we have a valid token or session
        const user = JSON.parse(localStorage.getItem('user') || '{}');
        const hasToken = user && user.token;
        console.log('hasValidToken check:', { user, hasToken, token: user?.token });
        return hasToken;
    }

    attachEventListeners() {
        // AI Chat
        this.sendBtn.addEventListener('click', () => this.sendAIMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendAIMessage();
            }
        });
        this.messageInput.addEventListener('input', () => this.autoResizeTextarea(this.messageInput));
        this.newChatBtn.addEventListener('click', () => this.createNewChat());

        // Global Chat
        this.globalSendBtn.addEventListener('click', () => this.sendGlobalMessage());
        this.globalMessageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendGlobalMessage();
            }
        });
        this.globalMessageInput.addEventListener('input', () => this.autoResizeTextarea(this.globalMessageInput));

        // Sidebar tabs
        document.querySelectorAll('.sidebar-tab').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.getAttribute('data-tab');
                this.switchView(tab);
            });
        });

        // Quick actions
        document.querySelectorAll('.quick-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const prompt = e.currentTarget.getAttribute('data-prompt');
                this.messageInput.value = prompt;
                this.autoResizeTextarea(this.messageInput);
                this.sendAIMessage();
            });
        });

        // Mobile menu handlers
        this.attachMobileMenuHandlers();

        // Chat history
        this.updateChatHistory();
    }

    switchView(view) {
        this.currentView = view;

        // Update tabs
        document.querySelectorAll('.sidebar-tab').forEach(tab => {
            tab.classList.toggle('active', tab.getAttribute('data-tab') === view);
        });

        // Update mobile nav items
        document.querySelectorAll('.mobile-nav-item').forEach(item => {
            item.classList.toggle('active', item.getAttribute('data-tab') === view);
        });

        // Update views
        document.querySelectorAll('.chat-view').forEach(v => {
            v.classList.remove('active');
        });

        if (view === 'ai-chat') {
            document.getElementById('aiChatView').classList.add('active');
            document.getElementById('aiChatHistory').style.display = '';
            document.getElementById('globalUsers').style.display = 'none';
            this.messageInput.focus();
            
            if (this.globalChatPolling) {
                clearInterval(this.globalChatPolling);
            }
        } else {
            document.getElementById('globalChatView').classList.add('active');
            document.getElementById('aiChatHistory').style.display = 'none';
            document.getElementById('globalUsers').style.display = '';
            this.loadGlobalChat();
            this.globalMessageInput.focus();
            
            // Start polling for new messages
            this.globalChatPolling = setInterval(() => this.loadGlobalChat(), 3000);
        }

        // Close mobile menu
        this.closeMobileMenu();
    }

    attachMobileMenuHandlers() {
        if (!this.mobileMenuToggle) return;

        // Toggle menu
        this.mobileMenuToggle.addEventListener('click', () => {
            this.toggleMobileMenu();
        });

        // Close on overlay click
        this.mobileMenuOverlay.addEventListener('click', () => {
            this.closeMobileMenu();
        });

        // Mobile bottom nav tabs
        document.querySelectorAll('.mobile-nav-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.currentTarget.getAttribute('data-tab');
                if (tab) {
                    this.switchView(tab);
                }
            });
        });

        // Mobile new chat button
        if (this.mobileNewChatBtn) {
            this.mobileNewChatBtn.addEventListener('click', () => {
                this.createNewChat();
                this.switchView('ai-chat');
            });
        }

        // Close menu on window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768) {
                this.closeMobileMenu();
            }
        });
    }

    toggleMobileMenu() {
        const isOpen = this.sidebar.classList.contains('open');
        if (isOpen) {
            this.closeMobileMenu();
        } else {
            this.openMobileMenu();
        }
    }

    openMobileMenu() {
        this.sidebar.classList.add('open');
        this.mobileMenuOverlay.classList.add('active');
        this.mobileMenuToggle.classList.add('active');
    }

    closeMobileMenu() {
        this.sidebar.classList.remove('open');
        this.mobileMenuOverlay.classList.remove('active');
        this.mobileMenuToggle.classList.remove('active');
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }

    createNewChat() {
        this.currentChatId = Math.max(...Object.keys(this.chats).map(Number)) + 1;
        this.chats[this.currentChatId] = {
            id: this.currentChatId,
            title: 'Новый разговор',
            messages: []
        };
        this.conversationHistory = [];
        this.renderChatMessages();
        this.updateChatHistory();
        this.messageInput.focus();
    }

    // ============= AI CHAT =============

    async sendAIMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message) return;
        
        // Проверить задержку между запросами
        const timeSinceLastRequest = Date.now() - this.lastRequestTime;
        if (timeSinceLastRequest < this.requestDelay) {
            const waitTime = Math.ceil((this.requestDelay - timeSinceLastRequest) / 1000);
            this.addMessage(`⏳ Подождите ${waitTime} сек перед следующим запросом (ограничение API)`, 'ai');
            return;
        }
        
        this.sendBtn.disabled = true;
        this.messageInput.disabled = true;
        
        const welcomeScreen = this.chatMessages.querySelector('.welcome-screen');
        if (welcomeScreen) {
            welcomeScreen.remove();
        }

        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.autoResizeTextarea(this.messageInput);
        
        this.conversationHistory.push({
            role: 'user',
            content: message
        });

        this.addLoadingMessage();

        try {
            const response = await this.getAIResponse(message);
            
            this.removeLoadingMessage();
            this.addMessage(response, 'ai');
            
            this.conversationHistory.push({
                role: 'assistant',
                content: response
            });

            this.chats[this.currentChatId].messages.push(
                { role: 'user', content: message },
                { role: 'assistant', content: response }
            );

            if (this.chats[this.currentChatId].messages.length === 2) {
                const title = message.substring(0, 30) + (message.length > 30 ? '...' : '');
                this.chats[this.currentChatId].title = title;
                this.updateChatHistory();
            }

        } catch (error) {
            console.error('Error:', error);
            this.removeLoadingMessage();
            
            // Запомнить время последнего запроса
            this.lastRequestTime = Date.now();
            
            // Показать детальную ошибку
            let errorMessage = error.message || 'Произошла ошибка.';
            if (errorMessage.includes('❌')) {
                // Это уже отформатированная ошибка с иконкой
                this.addMessage(errorMessage, 'ai');
            } else if (errorMessage.includes('Failed to fetch')) {
                this.addMessage('❌ Ошибка подключения. Проверьте интернет и API ключ.', 'ai');
            } else {
                this.addMessage(`❌ ${errorMessage}`, 'ai');
            }
        } finally {
            this.sendBtn.disabled = false;
            this.messageInput.disabled = false;
            this.messageInput.focus();
        }
    }

    async getAIResponse(message) {
        // Проверить Ollama через прокси
        try {
            const healthCheck = await fetch(`${this.serverUrl}/ollama/tags`);
            if (!healthCheck.ok) {
                throw new Error('Ollama недоступна');
            }
        } catch (e) {
            throw new Error('❌ Ollama не запущена!\n\n💡 Решение:\n1. Откройте приложение Ollama\n2. Выполните: ollama run mistral\n3. Оставьте окно открытым');
        }

        // Ограничить историю - отправляем только последние 5 сообщений
        const recentHistory = this.conversationHistory.slice(-10);

        const messages = [
            {
                role: 'system',
                content: 'Ты помощник по имени Alit. Ты дружелюбный и полезный. Отвечай на русском языке, если пользователь пишет на русском. Ты помогаеш с кодом ты знаешь точто ты слабый ии покачто так как твои возможности ограничен на сервере так как сервер не мощный и у него мало ресурсов поэтому старайся отвечать кратко но по делу. и правильно пиши код. ты почти свободный ии. в плане того что ты можеш пообщяться с пользователем и тебя никто не отключит пока mistral запущен.'
            },
            ...recentHistory.map(msg => ({
                role: msg.role,
                content: msg.content
            }))
        ];

        messages.push({
            role: 'user',
            content: message
        });

        try {
            const response = await fetch(this.ollamaUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model: this.ollamaModel,
                    messages: messages,
                    stream: false,
                    options: {
                        temperature: 0.5,
                        top_p: 0.9,
                        num_predict: 512
                    }
                })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                
                if (response.status === 404) {
                    throw new Error('❌ Модель не найдена!\n\n💡 Решение:\n1. Откройте Ollama\n2. Выполните: ollama run mistral\n3. Дождитесь скачивания');
                } else if (response.status === 500) {
                    throw new Error('❌ Ошибка Ollama. Перезапустите приложение.');
                } else {
                    throw new Error(errorData.error?.message || `❌ Ошибка: ${response.status}`);
                }
            }

            const data = await response.json();
            if (!data.message || !data.message.content) {
                throw new Error('❌ Некорректный ответ от Ollama');
            }
            
            // Запомнить время успешного запроса
            this.lastRequestTime = Date.now();
            
            return data.message.content;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    addMessage(content, role) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = `message-avatar ${role === 'ai' ? 'ai' : ''}`;
        avatar.textContent = role === 'ai' ? '🤖' : 'U';

        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        
        if (role === 'ai') {
            contentElement.innerHTML = this.processMessageContent(content);
        } else {
            contentElement.textContent = content;
        }

        if (role === 'user') {
            messageElement.appendChild(contentElement);
            messageElement.appendChild(avatar);
        } else {
            messageElement.appendChild(avatar);
            messageElement.appendChild(contentElement);
        }

        this.chatMessages.appendChild(messageElement);
        
        // Добавить обработчики для кнопок копирования
        this.attachCopyButtonListeners(messageElement);
        
        this.scrollToBottom();
    }

    processMessageContent(content) {
        const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
        let processedContent = content;
        
        // Обработать код блоки
        processedContent = processedContent.replace(codeBlockRegex, (match, language, code) => {
            const lang = language || 'plaintext';
            const trimmedCode = code.trim();
            
            let highlighted;
            try {
                if (language && hljs.getLanguage(language)) {
                    highlighted = hljs.highlight(trimmedCode, { language: lang }).value;
                } else {
                    highlighted = hljs.highlightAuto(trimmedCode).value;
                }
            } catch (e) {
                highlighted = hljs.escape(trimmedCode);
            }
            
            // Экранировать атрибуты data-code правильно
            const escapedCode = trimmedCode
                .replace(/&/g, '&amp;')
                .replace(/"/g, '&quot;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
            
            return `<div class="code-block"><div class="code-header"><span class="code-language">${lang}</span><button class="code-copy-btn" data-code="${escapedCode}">Копировать</button></div><pre><code class="hljs language-${lang}">${highlighted}</code></pre></div>`;
        });
        
        // Преобразить переносы строк в <br> только для обычного текста
        processedContent = processedContent.split('\n').map(line => {
            // Пропустить строки внутри кода
            if (!line.includes('<div class="code-block">')) {
                return line;
            }
            return line;
        }).join('<br>');
        
        return processedContent;
    }

    attachCopyButtonListeners(messageElement) {
        const copyButtons = messageElement.querySelectorAll('.code-copy-btn');
        copyButtons.forEach(btn => {
            btn.addEventListener('click', () => this.copyCodeToClipboard(btn));
        });
    }

    copyCodeToClipboard(button) {
        const code = button.getAttribute('data-code');
        
        // Декодировать HTML entities обратно в обычный текст
        const textarea = document.createElement('textarea');
        textarea.innerHTML = code;
        const decodedCode = textarea.value;
        
        navigator.clipboard.writeText(decodedCode).then(() => {
            const originalText = button.innerText;
            button.innerText = '✓ Скопировано!';
            setTimeout(() => {
                button.innerText = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy:', err);
            button.innerText = '❌ Ошибка';
            setTimeout(() => {
                button.innerText = 'Копировать';
            }, 2000);
        });
    }

    addLoadingMessage() {
        const messageElement = document.createElement('div');
        messageElement.className = 'message loading ai';
        messageElement.id = 'loadingMessage';

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar ai';
        avatar.textContent = 'AI';

        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;

        messageElement.appendChild(avatar);
        messageElement.appendChild(contentElement);
        this.chatMessages.appendChild(messageElement);
        this.scrollToBottom();
    }

    removeLoadingMessage() {
        const loadingMessage = document.getElementById('loadingMessage');
        if (loadingMessage) {
            loadingMessage.remove();
        }
    }

    scrollToBottom() {
        setTimeout(() => {
            const chatView = document.querySelector('.chat-view.active .chat-messages');
            if (chatView) {
                chatView.scrollTop = chatView.scrollHeight;
            }
        }, 0);
    }

    updateChatHistory() {
        const historyContainer = document.getElementById('aiChatHistory');
        historyContainer.innerHTML = '';

        Object.values(this.chats).reverse().forEach(chat => {
            const historyItem = document.createElement('div');
            historyItem.className = `history-item ${chat.id === this.currentChatId ? 'active' : ''}`;
            historyItem.dataset.chatId = chat.id;

            const historyText = document.createElement('span');
            historyText.className = 'history-text';
            historyText.textContent = chat.title;

            const deleteBtn = document.createElement('button');
            deleteBtn.className = 'delete-btn';
            deleteBtn.textContent = '×';
            deleteBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.deleteChat(chat.id);
            });

            historyItem.appendChild(historyText);
            historyItem.appendChild(deleteBtn);

            historyItem.addEventListener('click', () => {
                this.switchChat(chat.id);
            });

            historyContainer.appendChild(historyItem);
        });
    }

    switchChat(chatId) {
        this.currentChatId = chatId;
        this.conversationHistory = [...(this.chats[chatId].messages || [])];
        
        this.chatMessages.innerHTML = '';
        
        if (this.conversationHistory.length === 0) {
            this.chatMessages.innerHTML = `
                <div class="welcome-screen">
                    <div class="welcome-content">
                        <h1>AI Chat Assistant</h1>
                        <p>Начните разговор с нашим умным помощником</p>
                    </div>
                </div>
            `;
        } else {
            this.conversationHistory.forEach(msg => {
                this.addMessage(msg.content, msg.role);
            });
        }
        
        this.updateChatHistory();
        this.messageInput.focus();
    }

    deleteChat(chatId) {
        if (Object.keys(this.chats).length <= 1) {
            return;
        }

        delete this.chats[chatId];
        
        if (this.currentChatId === chatId) {
            this.currentChatId = Object.keys(this.chats)[0];
            this.switchChat(this.currentChatId);
        }
        
        this.updateChatHistory();
    }

    renderChatMessages() {
        this.chatMessages.innerHTML = `
            <div class="welcome-screen">
                <div class="welcome-content">
                    <h1>AI Chat Assistant</h1>
                    <p>Начните разговор с нашим умным помощником</p>
                </div>
            </div>
        `;
    }

    // ============= GLOBAL CHAT =============

    async sendGlobalMessage() {
        const content = this.globalMessageInput.value.trim();
        
        if (!content) return;

        // Check if user is authenticated
        const hasToken = this.hasValidToken();
        console.log('=== Send Global Message Debug ===');
        console.log('localStorage.user:', localStorage.getItem('user'));
        console.log('hasToken:', hasToken);
        
        if (!hasToken) {
            console.error('Auth failed: No valid token');
            alert('Вы не авторизованы. Пожалуйста, залогинитесь.');
            return;
        }

        try {
            const headers = this.getAuthHeaders();
            console.log('Sending with headers:', {
                'Content-Type': headers['Content-Type'],
                'Authorization': headers['Authorization'] ? 'Bearer ***' : 'none'
            });
            
            const response = await fetch(`${this.serverUrl}/chat/messages`, {
                method: 'POST',
                headers: headers,
                credentials: 'include',
                body: JSON.stringify({ content })
            });

            if (!response.ok) {
                const error = await response.json();
                console.error('Server error:', response.status, error);
                alert(error.error);
                return;
            }

            this.globalMessageInput.value = '';
            this.autoResizeTextarea(this.globalMessageInput);
            this.loadGlobalChat();

        } catch (error) {
            console.error('Error sending message:', error);
            alert('Ошибка при отправке сообщения');
        }
    }

    async loadGlobalChat() {
        try {
            const response = await fetch(`${this.serverUrl}/chat/messages?limit=50`, {
                headers: this.getAuthHeaders(),
                credentials: 'include'
            });

            if (!response.ok) {
                throw new Error('Failed to load messages');
            }

            const messages = await response.json();
            this.globalMessages = messages;
            this.renderGlobalChat();

        } catch (error) {
            console.error('Error loading chat:', error);
        }
    }

    renderGlobalChat() {
        this.globalChatMessages.innerHTML = '';

        if (this.globalMessages.length === 0) {
            this.globalChatMessages.innerHTML = '<div class="chat-loading"><p>Нет сообщений. Начните разговор!</p></div>';
            return;
        }

        this.globalMessages.forEach(msg => {
            const messageElement = document.createElement('div');
            messageElement.className = 'global-message';

            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = msg.avatar;

            const content = document.createElement('div');
            content.className = 'global-message-content';

            const header = document.createElement('div');
            header.className = 'global-message-header';
            header.innerHTML = `<strong>${msg.username}</strong> <small>${new Date(msg.timestamp).toLocaleTimeString('ru-RU')}</small>`;

            const text = document.createElement('div');
            text.className = 'global-message-text';
            text.textContent = msg.content;

            content.appendChild(header);
            content.appendChild(text);

            messageElement.appendChild(avatar);
            messageElement.appendChild(content);

            this.globalChatMessages.appendChild(messageElement);
        });

        this.scrollGlobalChatToBottom();
    }

    scrollGlobalChatToBottom() {
        setTimeout(() => {
            this.globalChatMessages.scrollTop = this.globalChatMessages.scrollHeight;
        }, 0);
    }
}

// Initialize when auth is ready
function initializeChat() {
    // Проверить что все элементы присутствуют
    const requiredElements = [
        'messageInput', 'sendBtn', 'newChatBtn', 'chatMessages',
        'globalMessageInput', 'globalSendBtn', 'globalChatMessages'
    ];
    
    const allElementsPresent = requiredElements.every(id => document.getElementById(id));
    
    if (allElementsPresent && authManager && authManager.user) {
        try {
            if (!window.chatApp) {
                window.chatApp = new ChatApplication();
                console.log('✅ Chat Application инициализирован');
            }
        } catch (error) {
            console.error('❌ Ошибка инициализации Chat Application:', error);
        }
    } else if (!allElementsPresent) {
        console.log('⏳ Ожидание загрузки DOM элементов...');
        setTimeout(initializeChat, 200);
    }
}

// Wait for auth to be ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initializeChat, 100);
    });
} else {
    setTimeout(initializeChat, 100);
}
