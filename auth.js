// Authentication Module
class AuthManager {
    constructor() {
        // Получить базовый URL сервера (может быть localhost или IP адрес)
        const protocol = window.location.protocol;
        const host = window.location.hostname;
        const baseUrl = `${protocol}//${host}:5000`;
        this.apiUrl = `${baseUrl}/api/auth`;
        
        this.user = null;
        this.initializeEventListeners();
        this.checkAuthStatus();
    }

    initializeEventListeners() {
        // Auth tabs
        document.querySelectorAll('.auth-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const tab = e.target.getAttribute('data-tab');
                this.switchAuthTab(tab);
            });
        });

        // Forms
        document.getElementById('loginForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleLogin();
        });

        document.getElementById('registerForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleRegister();
        });

        // Logout
        document.getElementById('logoutBtn').addEventListener('click', () => this.handleLogout());
        document.getElementById('logoutBtnModal').addEventListener('click', () => this.handleLogout());

        // Profile button
        document.getElementById('profileBtn').addEventListener('click', () => this.openProfileModal());
        document.getElementById('profileClose').addEventListener('click', () => this.closeProfileModal());
    }

    switchAuthTab(tab) {
        // Update buttons
        document.querySelectorAll('.auth-tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-tab') === tab);
        });

        // Update forms
        document.querySelectorAll('.auth-form').forEach(form => {
            form.classList.toggle('active', form.id === (tab === 'login' ? 'loginForm' : 'registerForm'));
        });

        // Clear errors
        document.getElementById('loginError').textContent = '';
        document.getElementById('registerError').textContent = '';
    }

    async handleLogin() {
        const username = document.getElementById('loginUsername').value.trim();
        const password = document.getElementById('loginPassword').value.trim();
        const errorEl = document.getElementById('loginError');

        try {
            const response = await fetch(`${this.apiUrl}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (!response.ok) {
                errorEl.textContent = data.error;
                return;
            }

            // Save user data (token is now inside user object)
            this.user = data.user;
            console.log('Login successful, user data:', this.user);
            localStorage.setItem('user', JSON.stringify(this.user));
            console.log('Stored in localStorage:', JSON.parse(localStorage.getItem('user')));

            // Close modal and show main
            this.showMainApp();
            this.updateUserUI();

        } catch (error) {
            errorEl.textContent = 'Ошибка подключения к серверу';
        }
    }

    async handleRegister() {
        const username = document.getElementById('registerUsername').value.trim();
        const email = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value.trim();
        const passwordConfirm = document.getElementById('registerPasswordConfirm').value.trim();
        const errorEl = document.getElementById('registerError');

        // Validation
        if (password !== passwordConfirm) {
            errorEl.textContent = 'Пароли не совпадают';
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, email, password })
            });

            const data = await response.json();

            if (!response.ok) {
                errorEl.textContent = data.error;
                return;
            }

            // Save user data with token (already in data.user)
            this.user = data.user || {};
            console.log('Registration successful, user data:', this.user);
            localStorage.setItem('user', JSON.stringify(this.user));
            console.log('Stored in localStorage:', JSON.parse(localStorage.getItem('user')));

            // Auto-login
            this.showMainApp();
            this.updateUserUI();

        } catch (error) {
            errorEl.textContent = 'Ошибка подключения к серверу';
        }
    }

    async handleLogout() {
        try {
            const headers = { 'Content-Type': 'application/json' };
            // Send token in logout if available
            if (this.user && this.user.token) {
                headers['Authorization'] = `Bearer ${this.user.token}`;
            }

            await fetch(`${this.apiUrl}/logout`, {
                method: 'POST',
                headers,
                credentials: 'include'
            });

            this.user = null;
            localStorage.removeItem('user');

            // Show auth modal
            document.getElementById('authModal').classList.add('active');
            document.getElementById('mainContainer').style.display = 'none';

            // Reset forms
            document.getElementById('loginForm').reset();
            document.getElementById('registerForm').reset();

            // Close modals
            this.closeProfileModal();

        } catch (error) {
            console.error('Logout error:', error);
        }
    }

    checkAuthStatus() {
        const savedUser = localStorage.getItem('user');
        if (savedUser) {
            this.user = JSON.parse(savedUser);
            this.showMainApp();
            this.updateUserUI();
        } else {
            // Try to restore session from server if cookie exists
            this.restoreSessionFromServer();
        }
    }

    async restoreSessionFromServer() {
        try {
            const response = await fetch(`${this.apiUrl}/user`, {
                method: 'GET',
                credentials: 'include'
            });

            if (response.ok) {
                const user = await response.json();
                console.log('Session restored from server:', user);
                this.user = user;
                localStorage.setItem('user', JSON.stringify(user));
                console.log('User saved to localStorage:', JSON.parse(localStorage.getItem('user')));
                this.showMainApp();
                this.updateUserUI();
            } else {
                console.log('Session restore failed with status:', response.status);
            }
        } catch (error) {
            console.log('No session found, showing login:', error);
        }
    }

    showMainApp() {
        document.getElementById('authModal').classList.remove('active');
        document.getElementById('mainContainer').style.display = 'flex';
        // Инициализировать приложение после показа интерфейса
        if (window.initializeChat) {
            setTimeout(() => window.initializeChat(), 200);
        }
    }

    updateUserUI() {
        if (!this.user) return;

        const avatar = this.user.username.charAt(0).toUpperCase();

        // Update sidebar
        document.getElementById('profileAvatar').textContent = avatar;
        document.getElementById('profileName').textContent = this.user.username;
        document.getElementById('profileEmail').textContent = this.user.email;

        // Update mobile avatar
        const mobileAvatar = document.getElementById('mobileAvatar');
        if (mobileAvatar) {
            mobileAvatar.textContent = avatar;
        }

        // Update profile modal
        document.getElementById('profileAvatarLarge').textContent = avatar;
        document.getElementById('profileUsernameDisplay').textContent = this.user.username;
        document.getElementById('profileEmailDisplay').textContent = this.user.email;
    }

    openProfileModal() {
        document.getElementById('profileModal').classList.add('active');
    }

    closeProfileModal() {
        document.getElementById('profileModal').classList.remove('active');
    }
}

// Initialize auth manager
const authManager = new AuthManager();
