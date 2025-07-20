// Global variables
let students = [];
let subjects = [];
let currentUser = null;
let stream = null;
let isCameraActive = false;
let selectedSubject = null;

// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const STUDENTS_API = `${API_BASE_URL}/database/students/`;
const SUBJECTS_API = `${API_BASE_URL}/database/subjects/`;
const ATTENDANCE_API = `${API_BASE_URL}/detection/attendance-confidence/`;
const USER_API = `${API_BASE_URL}/users/profile/`;
const MY_SUBJECTS_API = `${API_BASE_URL}/database/student/my-subjects/`;
const ATTENDANCE_HISTORY_API = `${API_BASE_URL}/database/attendance/history/`;

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

    // Camera controls
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    const startAttendanceBtn = document.getElementById('startAttendanceBtn');

    if (startCameraBtn) {
        startCameraBtn.addEventListener('click', startCamera);
    }
    if (stopCameraBtn) {
        stopCameraBtn.addEventListener('click', stopCamera);
    }
    if (startAttendanceBtn) {
        startAttendanceBtn.addEventListener('click', startAttendance);
    }

    // Subject selection
    const subjectSelect = document.getElementById('subjectSelect');
    if (subjectSelect) {
        subjectSelect.addEventListener('change', handleSubjectChange);
    }
}

// Load dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadUserInfo(),
            loadSubjects(),
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

    const studentName = document.getElementById('studentName');
    const userName = document.getElementById('userName');

    if (studentName) {
        studentName.textContent = currentUser.full_name || currentUser.username || 'Sinh viên';
    }
    if (userName) {
        userName.textContent = currentUser.full_name || currentUser.username || 'Sinh viên';
    }
}

// Load subjects
async function loadSubjects() {
    try {
        // Load student's registered subjects instead of all subjects
        const response = await makeAuthenticatedRequest(MY_SUBJECTS_API);
        if (response && response.ok) {
            const result = await response.json();

            // Handle the API response format: {success: true, data: [...]}
            if (result.success && result.data) {
                subjects = result.data;
            } else if (Array.isArray(result)) {
                subjects = result;
            } else {
                subjects = [];
            }

            // Store in global variable for statistics
            window.currentSubjects = subjects;

            updateSubjectSelect();
        }
    } catch (error) {
        console.error('Error loading subjects:', error);
        subjects = [];
        window.currentSubjects = [];
        updateSubjectSelect();
    }
}

// Update subject select dropdown
function updateSubjectSelect() {
    const subjectSelect = document.getElementById('subjectSelect');
    if (!subjectSelect) return;

    // Clear existing options except the first one
    subjectSelect.innerHTML = '<option value="">-- Chọn môn học --</option>';

    subjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject.id;
        option.textContent = `${subject.subject_code} - ${subject.subject_name}`;
        subjectSelect.appendChild(option);
    });
}

// Handle subject change
function handleSubjectChange() {
    const subjectSelect = document.getElementById('subjectSelect');
    const selectedSubjectInfo = document.getElementById('selectedSubjectInfo');

    if (!subjectSelect || !selectedSubjectInfo) return;

    const subjectId = subjectSelect.value;

    if (subjectId) {
        selectedSubject = subjects.find(s => s.id == subjectId);
        if (selectedSubject) {
            displaySubjectInfo(selectedSubject);
            selectedSubjectInfo.style.display = 'block';
        }
    } else {
        selectedSubject = null;
        selectedSubjectInfo.style.display = 'none';
    }
}

// Display subject information
function displaySubjectInfo(subject) {
    const teacherName = document.getElementById('teacherName');
    const classTime = document.getElementById('classTime');
    const classroom = document.getElementById('classroom');

    if (teacherName) {
        teacherName.textContent = subject.teacher_name || 'Chưa phân công';
    }
    if (classTime) {
        classTime.textContent = subject.schedule || 'Chưa có lịch học';
    }
    if (classroom) {
        classroom.textContent = subject.classroom || 'Chưa phân phòng';
    }
}

// Load statistics
async function loadStatistics() {
    try {
        // Load attendance history to calculate statistics
        const response = await makeAuthenticatedRequest(ATTENDANCE_HISTORY_API);
        if (response && response.ok) {
            const result = await response.json();

            // Ensure attendanceHistory is an array
            let attendanceHistory = [];
            if (Array.isArray(result)) {
                attendanceHistory = result;
            } else if (result && Array.isArray(result.data)) {
                attendanceHistory = result.data;
            }

            const totalAttendance = attendanceHistory.length;
            const presentCount = attendanceHistory.filter(a => a.status === 'present').length;
            const lateCount = attendanceHistory.filter(a => a.status === 'late').length;
            const attendanceRate = totalAttendance > 0 ? Math.round((presentCount / totalAttendance) * 100) : 0;

            // Get current subjects count from the global variable
            const currentSubjects = window.currentSubjects || subjects || [];

            const stats = {
                totalAttendance: totalAttendance,
                registeredSubjects: currentSubjects.length,
                attendanceRate: attendanceRate,
                lateCount: lateCount
            };

            updateStatistics(stats);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        // Use empty statistics if API fails
        const currentSubjects = window.currentSubjects || subjects || [];
        const stats = {
            totalAttendance: 0,
            registeredSubjects: currentSubjects.length,
            attendanceRate: 0,
            lateCount: 0
        };
        updateStatistics(stats);
    }
}

// Update statistics display
function updateStatistics(stats) {
    const totalAttendance = document.getElementById('totalAttendance');
    const registeredSubjects = document.getElementById('registeredSubjects');
    const attendanceRate = document.getElementById('attendanceRate');
    const lateCount = document.getElementById('lateCount');

    if (totalAttendance) totalAttendance.textContent = stats.totalAttendance;
    if (registeredSubjects) registeredSubjects.textContent = stats.registeredSubjects;
    if (attendanceRate) attendanceRate.textContent = `${stats.attendanceRate}%`;
    if (lateCount) lateCount.textContent = stats.lateCount;
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const response = await makeAuthenticatedRequest(ATTENDANCE_HISTORY_API);
        if (response && response.ok) {
            const result = await response.json();

            // Ensure attendanceHistory is an array
            let attendanceHistory = [];
            if (Array.isArray(result)) {
                attendanceHistory = result;
            } else if (result && Array.isArray(result.data)) {
                attendanceHistory = result.data;
            }

            // Convert attendance records to activity format
            const activities = attendanceHistory.slice(0, 5).map(record => {
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
                    desc: `Môn học: ${record.subject_name || 'Unknown'} - ${date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}`,
                    time: timeAgo
                };
            });

            displayRecentActivity(activities);
        }
    } catch (error) {
        console.error('Error loading recent activity:', error);
        // Show empty activity list if API fails
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

    if (activities.length === 0) {
        recentActivity.innerHTML = `
            <div class="activity-item">
                <div class="activity-icon info">
                    <i class="fas fa-info-circle"></i>
                </div>
                <div class="activity-content">
                    <div class="activity-title">Chưa có hoạt động</div>
                    <div class="activity-desc">Chưa có lịch sử điểm danh nào</div>
                    <div class="activity-time">-</div>
                </div>
            </div>
        `;
        return;
    }

    activities.forEach(activity => {
        const activityItem = document.createElement('div');
        activityItem.className = 'activity-item';
        activityItem.innerHTML = `
            <div class="activity-icon ${activity.type}">
                <i class="fas fa-${activity.type === 'success' ? 'check' : activity.type === 'warning' ? 'clock' : activity.type === 'error' ? 'times' : 'info-circle'}"></i>
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

// Camera functions
async function startCamera() {
    try {
        const video = document.getElementById('video');
        if (!video) return;

        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });

        video.srcObject = stream;

        // Fix camera mirror effect
        video.style.transform = 'scaleX(-1)';

        isCameraActive = true;

        // Update button states
        const startCameraBtn = document.getElementById('startCameraBtn');
        const stopCameraBtn = document.getElementById('stopCameraBtn');
        const startAttendanceBtn = document.getElementById('startAttendanceBtn');

        if (startCameraBtn) startCameraBtn.disabled = true;
        if (stopCameraBtn) stopCameraBtn.disabled = false;
        if (startAttendanceBtn) startAttendanceBtn.disabled = false;

        showToast('Camera đã được bật', 'success');
    } catch (error) {
        console.error('Error starting camera:', error);
        showToast('Không thể bật camera. Vui lòng kiểm tra quyền truy cập.', 'error');
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }

    const video = document.getElementById('video');
    if (video) {
        video.srcObject = null;
    }

    isCameraActive = false;

    // Update button states
    const startCameraBtn = document.getElementById('startCameraBtn');
    const stopCameraBtn = document.getElementById('stopCameraBtn');
    const startAttendanceBtn = document.getElementById('startAttendanceBtn');

    if (startCameraBtn) startCameraBtn.disabled = false;
    if (stopCameraBtn) stopCameraBtn.disabled = true;
    if (startAttendanceBtn) startAttendanceBtn.disabled = true;

    showToast('Camera đã được tắt', 'info');
}

// Start attendance
async function startAttendance() {
    if (!selectedSubject) {
        showToast('Vui lòng chọn môn học trước khi điểm danh', 'warning');
        return;
    }

    if (!isCameraActive) {
        showToast('Vui lòng bật camera trước khi điểm danh', 'warning');
        return;
    }

    try {
        showLoading(true);

        // Capture image from video
        const video = document.getElementById('video');
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0);

        // Convert canvas to blob and send
        canvas.toBlob(async (blob) => {
            try {
                // Create FormData for file upload
                const formData = new FormData();
                formData.append('image', blob, 'attendance.jpg');
                formData.append('subject_name', selectedSubject.subject_name);
                formData.append('student_code', currentUser.username);

                // Send attendance request
                const response = await makeAuthenticatedRequest(ATTENDANCE_API, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        // Remove Content-Type to let browser set it for FormData
                    }
                });

                if (response && response.ok) {
                    const result = await response.json();
                    showToast('Điểm danh thành công!', 'success');

                    // Update statistics
                    setTimeout(() => {
                        loadStatistics();
                        loadRecentActivity();
                    }, 1000);
                } else {
                    const error = await response.json();
                    showToast(error.message || 'Điểm danh thất bại', 'error');
                }
            } catch (error) {
                console.error('Attendance error:', error);
                showToast('Lỗi khi điểm danh. Vui lòng thử lại.', 'error');
            } finally {
                showLoading(false);
            }
        }, 'image/jpeg', 0.8);

    } catch (error) {
        console.error('Attendance error:', error);
        showToast('Lỗi khi điểm danh. Vui lòng thử lại.', 'error');
        showLoading(false);
    }
}

// Update user info display
function updateUserInfo() {
    if (!currentUser) return;

    const studentName = document.getElementById('studentName');
    const userName = document.getElementById('userName');

    if (studentName) {
        studentName.textContent = currentUser.full_name || currentUser.username || 'Sinh viên';
    }
    if (userName) {
        userName.textContent = currentUser.full_name || currentUser.username || 'Sinh viên';
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

// Loading state management
function showLoading(show) {
    const loadingOverlay = document.getElementById('loadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = show ? 'flex' : 'none';
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
        const response = await fetch(`${API_BASE_URL}/users/refresh/`, {
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

    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;

    alertContainer.appendChild(alert);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 3000);
} 