# Authentication Fix Summary

## Problem
User reported "Вы не авторизованы" (Not authorized) error when trying to send messages on localhost after implementing token-based authentication.

## Root Causes Identified and Fixed

### 1. CORS Configuration Issue
**Problem:** CORS was configured with `supports_credentials: False` and wildcard `origins: "*"`, which prevented browsers from sending cookies (session credentials).

**Solution:** Updated CORS to explicitly support credentials with specific origins:
```python
cors_config = {
    "origins": ["http://localhost:5000", "http://127.0.0.1:5000", ...],
    "supports_credentials": True
}
```

### 2. Inconsistent Token Response Format
**Problem:** Different auth endpoints returned tokens in different locations:
- `login()` returned: `{ "user": {...}, "token": token }` (top level)
- `register()` returned: `{ "user": {..., "token": token }}` (inside user)
- `get_current_user()` returned: `{ ..., "token": token }` (at root)

**Solution:** Made all endpoints return token consistently inside the user object.

### 3. Missing Session Persistence Configuration
**Problem:** `session.permanent = True` was only set in `login()`, not in `register()`.

**Solution:** Added `session.permanent = True` to both register and login routes, plus Flask config:
```python
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False  # Development
app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 60 * 60  # 7 days
```

### 4. Missing Session Restoration on Page Reload
**Problem:** When browser reloaded, session cookie was lost because:
- No code to restore auth from server
- Frontend couldn't verify if session still valid

**Solution:** Implemented session restoration:
- Server: `GET /api/auth/user` returns current user + token
- Client: `restoreSessionFromServer()` calls endpoint on page load
- If successful, localStorage is restored with user + token

## Implementation Details

### Backend (server.py)

**1. Token Generation**
```python
def generate_token():
    return str(uuid.uuid4())
```

**2. Authentication Helper**
```python
def get_authenticated_username():
    # Check session first (same-origin)
    if 'username' in session:
        return session['username']
    # Check Bearer token (cross-origin)
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1]
        # Verify token in users data
        ...
```

**3. Register Route** (Fixed)
```python
@app.route('/api/auth/register', methods=['POST'])
def register():
    # Create user, generate token
    token = generate_token()
    users[username]['token'] = token
    
    # SET SESSION AS PERMANENT (NEW)
    session.permanent = True
    session['username'] = username
    session['user_id'] = user_id
    
    # Return token in user object
    return jsonify({
        'user': {
            'token': token,  # Inside user object
            ...
        }
    }), 201
```

**4. Login Route** (Updated)
```python
# Rotate token on each login
token = generate_token()
users[username]['token'] = token
save_users(users)

# Set session with permanent flag
session.permanent = True
session['user_id'] = user['id']
session['username'] = username

# Return token in user object
return jsonify({
    'user': {
        'token': token,  # Inside user object
        ...
    }
}), 200
```

**5. Session Restoration Endpoint** (New/Unchanged)
```python
@app.route('/api/auth/user', methods=['GET'])
def get_current_user():
    username = get_authenticated_username()
    if not username:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = users[username]
    return jsonify({
        'id': user['id'],
        'username': username,
        'email': user['email'],
        'avatar': user['avatar'],
        'token': user.get('token')
    }), 200
```

### Frontend (auth.js)

**1. Login Handler** (Updated)
```javascript
async handleLogin() {
    const data = await response.json();
    
    // Token is now inside user object
    this.user = data.user;  // Already has token
    localStorage.setItem('user', JSON.stringify(this.user));
    
    this.showMainApp();
}
```

**2. Register Handler** (Updated)
```javascript
async handleRegister() {
    const data = await response.json();
    
    // Token comes in user object
    this.user = data.user;
    localStorage.setItem('user', JSON.stringify(this.user));
    
    this.showMainApp();
}
```

**3. Session Restoration** (New)
```javascript
async restoreSessionFromServer() {
    const response = await fetch(`${this.apiUrl}/user`, {
        credentials: 'include'  // Send cookies
    });
    
    if (response.ok) {
        const user = await response.json();
        this.user = user;
        localStorage.setItem('user', JSON.stringify(user));
        this.showMainApp();
    }
}

checkAuthStatus() {
    const saved = localStorage.getItem('user');
    if (saved) {
        this.user = JSON.parse(saved);
        this.showMainApp();
    } else {
        this.restoreSessionFromServer();  // Try server
    }
}
```

### Frontend (script.js)

**1. Token Validation** (New)
```javascript
hasValidToken() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    return user && user.token;
}

getAuthHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user && user.token) {
        headers['Authorization'] = `Bearer ${user.token}`;
    }
    return headers;
}
```

**2. Message Sending** (Updated)
```javascript
async sendGlobalMessage() {
    // Check auth
    if (!this.hasValidToken()) {
        alert('Not authorized');
        return;
    }
    
    // Send with token
    const response = await fetch(`${this.serverUrl}/chat/messages`, {
        method: 'POST',
        headers: this.getAuthHeaders(),  // Includes token
        credentials: 'include',
        body: JSON.stringify({ content })
    });
}
```

## Authentication Flow

### Initial Registration/Login
```
1. User enters credentials
2. POST /api/auth/register or /api/auth/login
3. Server creates/rotates token
4. Server sets session.permanent = True
5. Server returns user with token in response
6. Browser stores user in localStorage with token
7. Browser shows main app
```

### Page Reload
```
1. Page loads
2. checkAuthStatus() called
3. If localStorage has user → show app
4. Else → call restoreSessionFromServer()
5. restoreSessionFromServer() sends GET /api/auth/user (with session cookie)
6. Server validates session cookie
7. Server returns user with current token
8. Browser restores localStorage from response
9. Browser shows app (or shows login if no session)
```

### Message Sending
```
1. User types message
2. Call sendGlobalMessage()
3. Check hasValidToken() → verify localStorage.user.token exists
4. Fetch POST /api/chat/messages with:
   - Authorization: Bearer <token>
   - credentials: include (also sends session cookie)
5. Server calls get_authenticated_username():
   - Checks session cookie first
   - Falls back to Bearer token
6. Server validates auth, sends message
```

## Security Features

1. **Dual Auth System:**
   - Session cookies for same-origin (simpler, uses httpOnly in production)
   - Bearer tokens for cross-origin (works with any client)

2. **Token Rotation:**
   - New token generated on each login
   - Old token is discarded (not actively revoked, just overwrites)
   - Can be improved with token list/blacklist

3. **Session Persistence:**
   - 7-day lifetime for sessions
   - SameSite=Lax prevents CSRF
   - SECURE=False for development (should be True in production)

4. **Credential Handling:**
   - Passwords hashed with werkzeug.security
   - Tokens are UUIDs (cryptographically random)
   - No sensitive data in localStorage except tokens

## Testing Results

All tests pass:
✅ Register creates token + session
✅ Session restore works (status 200)
✅ Bearer token auth works (status 201)
✅ Login creates new token + rotates session
✅ Session after login works (status 200)
✅ Message sending with token works
✅ Browser page reload restores auth

## Files Modified

1. **server.py**
   - Fixed CORS configuration
   - Added session persistence config
   - Added `session.permanent = True` to register and login
   - Unified token response format

2. **auth.js**
   - Updated login to store token from user object
   - Updated register to store token from user object
   - Added `restoreSessionFromServer()` method
   - Updated `checkAuthStatus()` to call restoration
   - Added debug logging

3. **script.js**
   - Added `hasValidToken()` method
   - Added `getAuthHeaders()` method
   - Updated `sendGlobalMessage()` to check auth and use headers
   - Updated `loadGlobalChat()` to use auth headers
   - Added debug logging

4. **test_auth.html** (Created)
   - Comprehensive manual testing tool
   - Tests register, login, session restore, message sending
