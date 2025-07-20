// auth_check.js - Authentication utility for admin panel

function checkAuthToken() {
    const token = localStorage.getItem('accessToken');
    const refreshToken = localStorage.getItem('refreshToken');

    console.log('🔑 Auth Check:', {
        hasAccessToken: !!token,
        hasRefreshToken: !!refreshToken,
        tokenLength: token ? token.length : 0
    });

    if (!token) {
        console.warn('❌ No access token found');
        redirectToLogin();
        return false;
    }

    // Decode JWT payload to check expiration (basic check)
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Math.floor(Date.now() / 1000);

        console.log('📅 Token info:', {
            exp: payload.exp,
            currentTime: currentTime,
            expired: payload.exp < currentTime,
            timeLeft: payload.exp - currentTime
        });

        if (payload.exp < currentTime) {
            console.warn('⏰ Token expired, attempting refresh...');
            return refreshAuthToken();
        }

        return true;
    } catch (error) {
        console.error('❌ Invalid token format:', error);
        redirectToLogin();
        return false;
    }
}

async function refreshAuthToken() {
    const refreshToken = localStorage.getItem('refreshToken');

    if (!refreshToken) {
        console.warn('❌ No refresh token available');
        redirectToLogin();
        return false;
    }

    try {
        console.log('🔄 Attempting to refresh token...');
        const response = await fetch('http://localhost:8000/api/users/token/refresh/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                refresh: refreshToken
            })
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('accessToken', data.access);
            console.log('✅ Token refreshed successfully');
            return true;
        } else {
            console.error('❌ Token refresh failed:', response.status);
            redirectToLogin();
            return false;
        }
    } catch (error) {
        console.error('❌ Token refresh error:', error);
        redirectToLogin();
        return false;
    }
}

function redirectToLogin() {
    // Clear invalid tokens
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');

    // Show notification
    showNotification('Phiên đăng nhập đã hết hạn. Đang chuyển hướng...', 'warning');

    // Redirect after a short delay
    setTimeout(() => {
        window.location.href = '../login/login.html';
    }, 2000);
}

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelectorAll('.notification');
    existing.forEach(n => n.remove());

    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Style the notification
    Object.assign(notification.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '8px',
        color: 'white',
        fontWeight: '500',
        zIndex: '9999',
        maxWidth: '300px'
    });

    // Set background color based on type
    const colors = {
        success: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
        error: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        warning: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
        info: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    };

    notification.style.background = colors[type] || colors.info;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Auto-check token on page load
document.addEventListener('DOMContentLoaded', function () {
    console.log('🔐 Checking authentication...');
    checkAuthToken();
});

// Export functions for global use
window.checkAuthToken = checkAuthToken;
window.refreshAuthToken = refreshAuthToken;
window.redirectToLogin = redirectToLogin; 