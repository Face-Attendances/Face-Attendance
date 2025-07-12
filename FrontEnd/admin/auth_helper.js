// Authentication helper for admin panel
class AuthHelper {
    constructor() {
        this.API_BASE_URL = 'http://localhost:8000/api';
        this.token = localStorage.getItem('accessToken');
        this.refreshToken = localStorage.getItem('refreshToken');
    }

    // Check if token exists and is valid
    isAuthenticated() {
        return !!this.token;
    }

    // Get current token
    getToken() {
        return this.token;
    }

    // Login and get tokens
    async login(code, password) {
        try {
            const response = await fetch(`${this.API_BASE_URL}/users/login/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ code, password })
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access;
                this.refreshToken = data.refresh;

                localStorage.setItem('accessToken', this.token);
                localStorage.setItem('refreshToken', this.refreshToken);

                console.log('✅ Login successful');
                return true;
            } else {
                console.log('❌ Login failed:', data.message);
                return false;
            }
        } catch (error) {
            console.error('❌ Login error:', error);
            return false;
        }
    }

    // Refresh token
    async refreshAccessToken() {
        if (!this.refreshToken) {
            console.log('❌ No refresh token available');
            return false;
        }

        try {
            const response = await fetch(`${this.API_BASE_URL}/users/token/refresh/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ refresh: this.refreshToken })
            });

            const data = await response.json();

            if (response.ok) {
                this.token = data.access;
                localStorage.setItem('accessToken', this.token);
                console.log('✅ Token refreshed successfully');
                return true;
            } else {
                console.log('❌ Token refresh failed:', data.message);
                this.logout();
                return false;
            }
        } catch (error) {
            console.error('❌ Token refresh error:', error);
            this.logout();
            return false;
        }
    }

    // Logout
    logout() {
        this.token = null;
        this.refreshToken = null;
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        console.log('✅ Logged out');
    }

    // Make authenticated request with automatic token refresh
    async makeAuthenticatedRequest(url, options = {}) {
        if (!this.token) {
            console.log('❌ No token available');
            return null;
        }

        // Add authorization header
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${this.token}`
        };

        try {
            const response = await fetch(url, options);

            // If token expired, try to refresh
            if (response.status === 401) {
                console.log('🔄 Token expired, attempting refresh...');
                const refreshed = await this.refreshAccessToken();

                if (refreshed) {
                    // Retry request with new token
                    options.headers['Authorization'] = `Bearer ${this.token}`;
                    return await fetch(url, options);
                } else {
                    console.log('❌ Token refresh failed, redirecting to login');
                    window.location.href = '../login/login.html';
                    return null;
                }
            }

            return response;
        } catch (error) {
            console.error('❌ Request error:', error);
            return null;
        }
    }

    // Auto-login if token exists but is invalid
    async ensureAuthenticated() {
        if (!this.token) {
            console.log('🔐 No token found, attempting auto-login...');
            return await this.login('079205011306', 'Admin@123');
        }

        // Test current token
        const testResponse = await this.makeAuthenticatedRequest(`${this.API_BASE_URL}/database/students/`);
        if (testResponse && testResponse.status === 401) {
            console.log('🔐 Token invalid, attempting auto-login...');
            return await this.login('079205011306', 'Admin@123');
        }

        return true;
    }
}

// Create global instance
window.authHelper = new AuthHelper();

// Auto-ensure authentication when page loads
document.addEventListener('DOMContentLoaded', async () => {
    await window.authHelper.ensureAuthenticated();
}); 