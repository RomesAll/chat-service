const API_BASE = 'http://localhost:8000/api/v1';
const WS_BASE  = 'ws://localhost:8000';

// ============ TOKEN STORAGE ============
const TOKENS = {
    get access()  { return localStorage.getItem('access_token'); },
    get refresh() { return localStorage.getItem('refresh_token'); },
    get userId()  { return localStorage.getItem('user_id'); },

    save(access, refresh, userId) {
        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);
        localStorage.setItem('user_id', userId);
    },
    clear() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_id');
    },
    has() {
        return !!this.access && !!this.userId;
    }
};

// ============ ПАРОЛЬ ШИФРОВАНИЯ (тот же, что при входе) ============
// Хранится в sessionStorage — исчезает при закрытии вкладки.
const CRYPTO = {
    KEY: 'crypto_password',

    set(password) {
        sessionStorage.setItem(this.KEY, password);
    },
    get() {
        return sessionStorage.getItem(this.KEY);
    },
    clear() {
        sessionStorage.removeItem(this.KEY);
    },
    has() {
        return !!this.get();
    }
};

// ============ ПРОВЕРКА ТОКЕНОВ ============
// GET /check/access-tokens → 204 если ок
async function checkAccessToken() {
    const token = TOKENS.access;
    if (!token) return false;
    try {
        const res = await fetch(`${API_BASE}/check/access-tokens`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return res.status === 204;
    } catch (e) {
        return false;
    }
}

// GET /check/refresh-tokens → 204 если ок
async function checkRefreshToken() {
    const token = TOKENS.refresh;
    if (!token) return false;
    try {
        const res = await fetch(`${API_BASE}/check/refresh-tokens`, {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        return res.status === 204;
    } catch (e) {
        return false;
    }
}

// POST /auth/tokens/refresh
async function tryRefreshTokens() {
    const refresh = TOKENS.refresh;
    if (!refresh) return false;
    try {
        const res = await fetch(`${API_BASE}/auth/tokens/refresh`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${refresh}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                refresh_token: refresh,
                token_type: 'refresh_token'
            })
        });
        if (!res.ok) return false;
        const data = await res.json();
        const detail = data.detail || data;
        TOKENS.save(detail.access_token, detail.refresh_token, TOKENS.userId);
        return true;
    } catch (e) {
        return false;
    }
}

// Полная проверка: access → если невалид, refresh → если ок, обновить
async function ensureAuthorized() {
    if (!TOKENS.has()) return false;

    if (await checkAccessToken()) return true;

    if (await checkRefreshToken()) {
        const ok = await tryRefreshTokens();
        if (ok) return true;
    }

    TOKENS.clear();
    return false;
}