// Global variables
let isAuthenticating = false;

// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const LOGIN_API = `${API_BASE_URL}/users/login/`;
const REFRESH_API = `${API_BASE_URL}/users/refresh/`;

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    setupEventListeners();
    checkRememberMe();
    updateDateTime();
    setInterval(updateDateTime, 1000);
});

// Setup event listeners
function setupEventListeners() {
    // Login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    // Password toggle
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function () {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            const icon = togglePassword.querySelector('i');
            if (icon) {
                icon.className = type === 'password' ? 'fas fa-eye' : 'fas fa-eye-slash';
            }
        });
    }

    // Ẩn social login buttons - đã comment trong HTML
    /*
    const googleBtn = document.querySelector('[onclick="loginWithGoogle()"]');
    const microsoftBtn = document.querySelector('[onclick="loginWithMicrosoft()"]');
    
    if (googleBtn) {
        googleBtn.addEventListener('click', loginWithGoogle);
    }
    if (microsoftBtn) {
        microsoftBtn.addEventListener('click', loginWithMicrosoft);
    }
    */

    // Input validation
    const usernameInput = document.getElementById('username');
    if (usernameInput) {
        usernameInput.addEventListener('input', validateUsername);
        usernameInput.addEventListener('blur', validateUsername);
    }

    if (passwordInput) {
        passwordInput.addEventListener('input', validatePassword);
        passwordInput.addEventListener('blur', validatePassword);
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();

    if (isAuthenticating) {
        return;
    }

    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('rememberMe').checked;

    // Validate inputs
    if (!validateForm(username, password)) {
        return;
    }

    // Show loading state
    setLoadingState(true);
    isAuthenticating = true;

    try {
        const response = await fetch(LOGIN_API, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                code: username,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            // Save tokens
            localStorage.setItem('accessToken', data.access);
            localStorage.setItem('refreshToken', data.refresh);

            // Save remember me preference
            if (rememberMe) {
                localStorage.setItem('rememberMe', 'true');
                localStorage.setItem('savedUsername', username);
            } else {
                localStorage.removeItem('rememberMe');
                localStorage.removeItem('savedUsername');
            }

            // Get user role and redirect
            await handleSuccessfulLogin(data);
        } else {
            handleLoginError(data);
        }
    } catch (error) {
        console.error('Login error:', error);
        showMessage('Lỗi kết nối. Vui lòng thử lại.', 'error');
    } finally {
        setLoadingState(false);
        isAuthenticating = false;
    }
}

// Handle successful login
async function handleSuccessfulLogin(data) {
    try {
        // Get user info to determine role
        const userResponse = await fetch(`${API_BASE_URL}/users/profile/`, {
            headers: {
                'Authorization': `Bearer ${data.access}`
            }
        });

        if (userResponse.ok) {
            const userData = await userResponse.json();
            const role = userData.role || 'student';

            showMessage('Đăng nhập thành công!', 'success');

            // Redirect based on role
            setTimeout(() => {
                switch (role.toLowerCase()) {
                    case 'admin':
                        window.location.href = '../admin/overview.html';
                        break;
                    case 'teacher':
                        window.location.href = '../teacher/dashboard.html';
                        break;
                    case 'student':
                    default:
                        window.location.href = '../student/dashboard.html';
                        break;
                }
            }, 1000);
        } else {
            // Fallback to student dashboard
            showMessage('Đăng nhập thành công!', 'success');
            setTimeout(() => {
                window.location.href = '../student/dashboard.html';
            }, 1000);
        }
    } catch (error) {
        console.error('Error getting user info:', error);
        // Fallback to student dashboard
        showMessage('Đăng nhập thành công!', 'success');
        setTimeout(() => {
            window.location.href = '../student/dashboard.html';
        }, 1000);
    }
}

// Handle login error
function handleLoginError(data) {
    let message = 'Đăng nhập thất bại.';

    if (data.detail) {
        message = data.detail;
    } else if (data.error) {
        message = data.error;
    } else if (data.non_field_errors) {
        message = data.non_field_errors[0];
    } else if (data.username) {
        message = data.username[0];
    } else if (data.password) {
        message = data.password[0];
    }

    showMessage(message, 'error');
}

// Social login functions - Ẩn chức năng này
/*
function loginWithGoogle() {
    showMessage('Tính năng đăng nhập Google đang được phát triển', 'info');
}

function loginWithMicrosoft() {
    showMessage('Tính năng đăng nhập Microsoft đang được phát triển', 'info');
}
*/

// Form validation
function validateForm(username, password) {
    let isValid = true;

    // Validate username
    if (!username) {
        showFieldError('username', 'Vui lòng nhập mã số');
        isValid = false;
    } else if (username.length !== 12 || !/^\d+$/.test(username)) {
        showFieldError('username', 'Mã số phải có 12 chữ số');
        isValid = false;
    } else {
        clearFieldError('username');
    }

    // Validate password
    if (!password) {
        showFieldError('password', 'Vui lòng nhập mật khẩu');
        isValid = false;
    } else if (password.length < 6) {
        showFieldError('password', 'Mật khẩu phải có ít nhất 6 ký tự');
        isValid = false;
    } else {
        clearFieldError('password');
    }

    return isValid;
}

function validateUsername() {
    const input = document.getElementById('username');
    const value = input.value.trim();

    if (!value) {
        showFieldError('username', 'Vui lòng nhập mã số');
    } else if (value.length !== 12 || !/^\d+$/.test(value)) {
        showFieldError('username', 'Mã số phải có 12 chữ số');
    } else {
        clearFieldError('username');
    }
}

function validatePassword() {
    const input = document.getElementById('password');
    const value = input.value;

    if (!value) {
        showFieldError('password', 'Vui lòng nhập mật khẩu');
    } else if (value.length < 6) {
        showFieldError('password', 'Mật khẩu phải có ít nhất 6 ký tự');
    } else {
        clearFieldError('password');
    }
}

// Field error handling
function showFieldError(fieldName, message) {
    const input = document.getElementById(fieldName);
    const inputGroup = input.closest('.input-group');

    if (inputGroup) {
        // Remove existing error
        clearFieldError(fieldName);

        // Add error class
        input.classList.add('error');
        inputGroup.classList.add('error');

        // Create error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error';
        errorDiv.textContent = message;
        errorDiv.id = `${fieldName}Error`;

        inputGroup.appendChild(errorDiv);
    }
}

function clearFieldError(fieldName) {
    const input = document.getElementById(fieldName);
    const inputGroup = input.closest('.input-group');
    const errorDiv = document.getElementById(`${fieldName}Error`);

    if (inputGroup) {
        input.classList.remove('error');
        inputGroup.classList.remove('error');
    }

    if (errorDiv) {
        errorDiv.remove();
    }
}

// Loading state management
function setLoadingState(loading) {
    const loginBtn = document.getElementById('loginBtn');
    const btnText = loginBtn.querySelector('.btn-text');
    const loadingSpan = loginBtn.querySelector('.loading');

    if (loading) {
        btnText.style.display = 'none';
        loadingSpan.style.display = 'inline-flex';
        loginBtn.disabled = true;
    } else {
        btnText.style.display = 'inline';
        loadingSpan.style.display = 'none';
        loginBtn.disabled = false;
    }
}

// Remember me functionality
function checkRememberMe() {
    const rememberMe = localStorage.getItem('rememberMe');
    const savedUsername = localStorage.getItem('savedUsername');

    if (rememberMe === 'true' && savedUsername) {
        const usernameInput = document.getElementById('username');
        const rememberMeCheckbox = document.getElementById('rememberMe');

        if (usernameInput) {
            usernameInput.value = savedUsername;
        }
        if (rememberMeCheckbox) {
            rememberMeCheckbox.checked = true;
        }
    }
}

// DateTime display
function updateDateTime() {
    const now = new Date();
    const dateTimeElement = document.getElementById('currentDateTime');

    if (dateTimeElement) {
        const formatted = now.toLocaleString('vi-VN', {
            weekday: 'long',
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });

        dateTimeElement.textContent = `🕒 ${formatted}`;
    }
}

// Message display
function showMessage(message, type = 'info') {
    // Remove existing messages
    const existingError = document.getElementById('errorMessage');
    const existingSuccess = document.getElementById('successMessage');

    if (existingError) existingError.style.display = 'none';
    if (existingSuccess) existingSuccess.style.display = 'none';

    // Show new message
    const messageElement = document.getElementById(`${type === 'error' ? 'error' : 'success'}Message`);
    if (messageElement) {
        messageElement.textContent = message;
        messageElement.style.display = 'block';

        // Auto hide after 5 seconds
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 5000);
    }
}

// Utility functions
function logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('rememberMe');
    localStorage.removeItem('savedUsername');

    window.location.href = 'login.html';
}

// Add CSS for field errors
const style = document.createElement('style');
style.textContent = `
    .input-group.error .form-input {
        border-color: #f56565;
        box-shadow: 0 0 0 3px rgba(245, 101, 101, 0.1);
    }
    
    .field-error {
        color: #f56565;
        font-size: 0.75rem;
        margin-top: 4px;
        animation: slideIn 0.3s ease-out;
    }
    
    .form-input.error {
        border-color: #f56565;
    }
    
    .form-input.error:focus {
        border-color: #f56565;
        box-shadow: 0 0 0 3px rgba(245, 101, 101, 0.1);
    }
`;
document.head.appendChild(style); 