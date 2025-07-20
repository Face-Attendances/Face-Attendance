// Global variables
let teachers = [];
let subjects = [];
let students = [];
let currentUser = null;
let attendanceData = [];

// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const TEACHERS_API = `${API_BASE_URL}/database/teachers/`;
const SUBJECTS_API = `${API_BASE_URL}/database/subjects/`;
const STUDENTS_API = `${API_BASE_URL}/database/students/`;
const ATTENDANCE_API = `${API_BASE_URL}/detection/attendance/`;
const USER_API = `${API_BASE_URL}/auth/user/`;

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    checkAuthentication();
    setupEventListeners();
    loadDashboardData();
    updateDateTime();
    setInterval(updateDateTime, 1000);
});

// Authentication check
async function checkAuthentication() {
    const token = localStorage.getItem('accessToken');

    if (!token) {
        redirectToLogin();
        return;
    }

    try {
        const response = await fetch(USER_API, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            currentUser = await response.json();
            updateUserInfo();
        } else {
            redirectToLogin();
        }
    } catch (error) {
        console.error('Auth check error:', error);
        redirectToLogin();
    }
}

// Setup event listeners
function setupEventListeners() {
    // User menu
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userMenu = document.getElementById('userMenu');

    if (userMenuBtn && userMenu) {
        userMenuBtn.addEventListener('click', function () {
            userMenu.classList.toggle('show');
        });

        // Close menu when clicking outside
        document.addEventListener('click', function (event) {
            if (!userMenuBtn.contains(event.target) && !userMenu.contains(event.target)) {
                userMenu.classList.remove('show');
            }
        });
    }

    // Subject action buttons
    document.addEventListener('click', function (event) {
        if (event.target.matches('.btn-view-students')) {
            const subjectId = event.target.dataset.subjectId;
            viewSubjectStudents(subjectId);
        } else if (event.target.matches('.btn-start-attendance')) {
            const subjectId = event.target.dataset.subjectId;
            startAttendance(subjectId);
        }
    });
}

// Load dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadUserInfo(),
            loadTeachingSubjects(),
            loadStatistics(),
            loadRecentActivity()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Lỗi khi tải dữ liệu dashboard', 'error');
    }
}

// Load user information
async function loadUserInfo() {
    if (!currentUser) return;

    const teacherName = document.getElementById('teacherName');
    const userName = document.getElementById('userName');

    if (teacherName) {
        teacherName.textContent = currentUser.full_name || currentUser.username || 'Giảng viên';
    }
    if (userName) {
        userName.textContent = currentUser.full_name || currentUser.username || 'Giảng viên';
    }
}

// Load teaching subjects
async function loadTeachingSubjects() {
    try {
        const response = await makeAuthenticatedRequest(`${API_BASE_URL}/database/teacher-subjects/teaching/`);
        if (response && response.ok) {
            const result = await response.json();

            // Handle the API response format: {success: true, data: [...]}
            let teachingSubjects = [];
            if (result.success && result.data) {
                teachingSubjects = result.data;
            } else if (Array.isArray(result)) {
                teachingSubjects = result;
            }

            displayTeachingSubjects(teachingSubjects);
        } else {
            console.error('Failed to load teaching subjects:', response.status, response.statusText);
            displayTeachingSubjects([]);
        }
    } catch (error) {
        console.error('Error loading teaching subjects:', error);
        displayTeachingSubjects([]);
    }
}

// Display teaching subjects
function displayTeachingSubjects(subjects) {
    const teachingSubjects = document.getElementById('teachingSubjects');
    if (!teachingSubjects) return;

    teachingSubjects.innerHTML = '';

    // Ensure subjects is an array
    if (!Array.isArray(subjects)) {
        console.warn('Subjects is not an array:', subjects);
        subjects = [];
    }

    if (subjects.length === 0) {
        teachingSubjects.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-book"></i>
                <h3>Không có môn học nào</h3>
                <p>Bạn chưa được phân công giảng dạy môn học nào</p>
            </div>
        `;
        return;
    }

    subjects.forEach(subject => {
        const subjectItem = document.createElement('div');
        subjectItem.className = 'subject-item';
        subjectItem.innerHTML = `
            <div class="subject-info">
                <h4>${subject.subject_name || 'Unknown'}</h4>
                <p>${subject.schedule || 'Chưa có lịch'} | Phòng ${subject.classroom || 'Chưa phân phòng'}</p>
                <span class="student-count">${subject.student_count || 0} sinh viên</span>
            </div>
            <div class="subject-actions">
                <button class="btn btn-primary btn-sm btn-view-students" data-subject-id="${subject.id}">
                    <i class="fas fa-users"></i> Xem sinh viên
                </button>
                <button class="btn btn-success btn-sm btn-start-attendance" data-subject-id="${subject.id}">
                    <i class="fas fa-clipboard-check"></i> Điểm danh
                </button>
            </div>
        `;
        teachingSubjects.appendChild(subjectItem);
    });
}

// Load statistics
async function loadStatistics() {
    try {
        // Load teaching subjects to get total subjects
        const subjectsResponse = await makeAuthenticatedRequest(`${API_BASE_URL}/database/teacher-subjects/teaching/`);
        let totalSubjects = 0;
        let totalStudents = 0;

        if (subjectsResponse && subjectsResponse.ok) {
            const result = await subjectsResponse.json();

            // Handle the API response format: {success: true, data: [...]}
            let subjects = [];
            if (result.success && result.data) {
                subjects = result.data;
            } else if (Array.isArray(result)) {
                subjects = result;
            }

            // Ensure subjects is an array
            if (Array.isArray(subjects)) {
                totalSubjects = subjects.length;
                totalStudents = subjects.reduce((sum, subject) => sum + (subject.student_count || 0), 0);
            } else {
                console.warn('Subjects response is not an array:', subjects);
                totalSubjects = 0;
                totalStudents = 0;
            }
        }

        // Load today's attendance
        const today = new Date().toISOString().split('T')[0];
        const attendanceResponse = await makeAuthenticatedRequest(`${API_BASE_URL}/database/attendance/log/?date=${today}`);
        let todayAttendance = 0;
        let attendanceRate = 0;

        if (attendanceResponse && attendanceResponse.ok) {
            const attendanceLog = await attendanceResponse.json();
            todayAttendance = attendanceLog.length;
            const presentCount = attendanceLog.filter(a => a.status === 'present').length;
            attendanceRate = todayAttendance > 0 ? Math.round((presentCount / todayAttendance) * 100) : 0;
        }

        const stats = {
            totalSubjects: totalSubjects,
            totalStudents: totalStudents,
            todayAttendance: todayAttendance,
            attendanceRate: attendanceRate
        };

        updateStatistics(stats);
    } catch (error) {
        console.error('Error loading statistics:', error);
        // Use empty statistics if API fails
        const stats = {
            totalSubjects: 0,
            totalStudents: 0,
            todayAttendance: 0,
            attendanceRate: 0
        };
        updateStatistics(stats);
    }
}

// Update statistics display
function updateStatistics(stats) {
    const totalSubjects = document.getElementById('totalSubjects');
    const totalStudents = document.getElementById('totalStudents');
    const todayAttendance = document.getElementById('todayAttendance');
    const attendanceRate = document.getElementById('attendanceRate');

    if (totalSubjects) totalSubjects.textContent = stats.totalSubjects;
    if (totalStudents) totalStudents.textContent = stats.totalStudents;
    if (todayAttendance) todayAttendance.textContent = stats.todayAttendance;
    if (attendanceRate) attendanceRate.textContent = `${stats.attendanceRate}%`;
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const response = await makeAuthenticatedRequest(`${API_BASE_URL}/database/attendance/log/`);
        if (response && response.ok) {
            const attendanceLog = await response.json();

            // Convert attendance records to activity format
            const activities = attendanceLog.slice(0, 5).map(record => {
                const status = record.status;
                let type = 'info';
                let title = 'Điểm danh';

                if (status === 'present') {
                    type = 'success';
                    title = 'Điểm danh thành công';
                } else if (status === 'late') {
                    type = 'warning';
                    title = 'Điểm danh muộn';
                } else if (status === 'absent') {
                    type = 'error';
                    title = 'Vắng mặt';
                }

                const date = new Date(record.timestamp);
                const timeAgo = getTimeAgo(date);

                return {
                    type: type,
                    title: title,
                    desc: `${record.subject_name || 'Unknown'} - ${record.student_name || 'Unknown'}`,
                    time: timeAgo
                };
            });

            displayRecentActivity(activities);
        } else {
            displayRecentActivity([]);
        }
    } catch (error) {
        console.error('Error loading recent activity:', error);
        displayRecentActivity([]);
    }
}

// Helper function to get time ago
function getTimeAgo(date) {
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));

    if (diffInHours < 1) {
        return 'Vừa xong';
    } else if (diffInHours < 24) {
        return `${diffInHours} giờ trước`;
    } else if (diffInHours < 48) {
        return 'Hôm qua';
    } else {
        return date.toLocaleDateString('vi-VN');
    }
}

// Display recent activity
function displayRecentActivity(activities) {
    const recentActivity = document.getElementById('recentActivity');
    if (!recentActivity) return;

    recentActivity.innerHTML = '';

    activities.forEach(activity => {
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div class="activity-icon ${activity.type}">
                <i class="fas fa-${activity.type === 'success' ? 'check' : activity.type === 'warning' ? 'exclamation-triangle' : activity.type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            </div>
            <div class="activity-content">
                <div class="activity-title">${activity.title}</div>
                <div class="activity-desc">${activity.desc}</div>
                <div class="activity-time">${activity.time}</div>
            </div>
        `;
        recentActivity.appendChild(activityItem);
    });
}

// View subject students
function viewSubjectStudents(subjectId) {
    // This would typically open a modal or navigate to a student list page
    showToast('Chuyển đến trang quản lý sinh viên', 'info');
    setTimeout(() => {
        window.location.href = `student-management.html?subject=${subjectId}`;
    }, 1000);
}

// Start attendance
function startAttendance(subjectId) {
    // This would typically open an attendance interface
    showToast('Bắt đầu điểm danh', 'info');
    setTimeout(() => {
        window.location.href = `attendance-log.html?subject=${subjectId}`;
    }, 1000);
}

// Update user info display
function updateUserInfo() {
    if (!currentUser) return;

    const teacherName = document.getElementById('teacherName');
    const userName = document.getElementById('userName');

    if (teacherName) {
        teacherName.textContent = currentUser.full_name || currentUser.username || 'Giảng viên';
    }
    if (userName) {
        userName.textContent = currentUser.full_name || currentUser.username || 'Giảng viên';
    }
}

// Update date time display
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

// Authentication helper
async function makeAuthenticatedRequest(url, options = {}) {
    const token = localStorage.getItem('accessToken');

    if (!token) {
        redirectToLogin();
        return null;
    }

    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        }
    });

    if (response.status === 401) {
        // Token expired, try to refresh
        const refreshed = await refreshToken();
        if (refreshed) {
            return makeAuthenticatedRequest(url, options);
        } else {
            redirectToLogin();
            return null;
        }
    }

    return response;
}

// Refresh token
async function refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');

    if (!refreshToken) {
        return false;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
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
            return true;
        }
    } catch (error) {
        console.error('Token refresh error:', error);
    }

    return false;
}

// Redirect to login
function redirectToLogin() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    window.location.href = '../login/login.html';
}

// Logout function
function logout() {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    window.location.href = '../login/login.html';
}

// Toast notification
function showToast(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    alertContainer.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Add CSS for toast notifications
const style = document.createElement('style');
style.textContent = `
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 3000;
        animation: slideIn 0.3s ease-out;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        backdrop-filter: blur(10px);
        display: flex;
        align-items: center;
        gap: 8px;
        max-width: 400px;
    }

    .toast-success {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
    }

    .toast-error {
        background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
    }

    .toast-warning {
        background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
    }

    .toast-info {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(100%);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;
document.head.appendChild(style); 