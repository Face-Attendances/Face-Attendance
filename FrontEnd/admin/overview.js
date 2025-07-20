// overview.js - Dashboard functionality

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Global variables
let currentUser = null;
let dashboardData = {};

// Get authentication token
const token = localStorage.getItem('accessToken');

// Helper function to get fetch headers with authorization
function getAuthHeaders() {
    const token = localStorage.getItem('accessToken');
    const headers = {
        'Content-Type': 'application/json'
    };

    if (token) {
        headers['Authorization'] = 'Bearer ' + token;
    }

    return headers;
}

// Refresh token function
async function refreshToken() {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
        console.error('No refresh token found');
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
            console.log('Token refreshed successfully');
            return true;
        } else {
            console.error('Failed to refresh token');
            return false;
        }
    } catch (error) {
        console.error('Error refreshing token:', error);
        return false;
    }
}

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadDashboardData();
    loadRecentActivity();
    loadStatistics();
    setupEventListeners();
    loadTeachersForSelect();
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    document.getElementById('searchActivity').addEventListener('input', filterActivity);
    document.getElementById('filterActivity').addEventListener('change', filterActivity);
    document.getElementById('timeRange').addEventListener('change', loadStatistics);

    // Form submissions
    document.getElementById('addStudentForm').addEventListener('submit', handleAddStudent);
    document.getElementById('addTeacherForm').addEventListener('submit', handleAddTeacher);
    document.getElementById('addSubjectForm').addEventListener('submit', handleAddSubject);

    // Modal close on outside click
    window.addEventListener('click', function (event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Load dashboard data
async function loadDashboardData() {
    console.log('🔄 Loading dashboard data...');
    console.log('🔑 Auth headers:', getAuthHeaders());
    console.log('🌐 API URL:', `${API_BASE_URL}/database/dashboard/stats/`);

    try {
        const response = await fetch(`${API_BASE_URL}/database/dashboard/stats/`, {
            headers: getAuthHeaders()
        });

        console.log('📡 Response status:', response.status);
        console.log('📡 Response headers:', response.headers);

        const data = await response.json();
        console.log('📊 Dashboard data received:', data);

        if (response.ok) {
            dashboardData = data;
            updateDashboardCards();
            console.log('✅ Dashboard data loaded successfully');
        } else {
            console.error('❌ API Error:', data);

            // Handle 401 Unauthorized - try to refresh token
            if (response.status === 401) {
                console.log('🔄 Token expired, attempting to refresh...');
                const refreshSuccess = await refreshToken();

                if (refreshSuccess) {
                    console.log('🔄 Retrying with new token...');
                    // Retry the request with new token
                    const retryResponse = await fetch(`${API_BASE_URL}/database/dashboard/stats/`, {
                        headers: getAuthHeaders()
                    });

                    if (retryResponse.ok) {
                        const retryData = await retryResponse.json();
                        dashboardData = retryData;
                        updateDashboardCards();
                        console.log('✅ Dashboard data loaded successfully after token refresh');
                        return;
                    }
                }

                showToast('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 'error');
                setTimeout(() => {
                    window.location.href = '../login/login.html';
                }, 2000);
            } else if (response.status === 404) {
                showToast('API endpoint không tồn tại', 'error');
            } else {
                showToast(`Lỗi API: ${data.error || data.detail || 'Unknown error'}`, 'error');
            }
        }
    } catch (error) {
        console.error('💥 Network/Parse Error:', error);
        showToast('Lỗi kết nối: ' + error.message, 'error');

        // Set default values to show something
        dashboardData = {
            total_students: 0,
            total_teachers: 0,
            total_subjects: 0,
            today_attendance: 0
        };
        updateDashboardCards();
    }
}

// Update dashboard cards
function updateDashboardCards() {
    document.getElementById('totalStudents').textContent = dashboardData.total_students || 0;
    document.getElementById('totalTeachers').textContent = dashboardData.total_teachers || 0;
    document.getElementById('totalSubjects').textContent = dashboardData.total_subjects || 0;
    document.getElementById('todayAttendance').textContent = dashboardData.today_attendance || 0;
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const response = await fetch(`${API_BASE_URL}/database/attendance/history/?days=7`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();

        if (data.success) {
            displayActivityTable(data.data);
        }
    } catch (error) {
        console.error('Error loading activity:', error);
        showToast('Lỗi khi tải hoạt động gần đây', 'error');
    }
}

// Display activity table
function displayActivityTable(activities) {
    const tbody = document.getElementById('activityTable');
    tbody.innerHTML = '';

    if (activities.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Không có hoạt động nào</td></tr>';
        return;
    }

    activities.forEach(activity => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDateTime(activity.timestamp)}</td>
            <td><span class="status-badge status-active">Điểm danh</span></td>
            <td>${activity.student_name} - ${activity.subject}</td>
            <td>${activity.detected_by_name || 'Hệ thống'}</td>
            <td>${activity.face_detection_confidence ? activity.face_detection_confidence.toFixed(1) + '%' : 'N/A'}</td>
        `;
        tbody.appendChild(row);
    });
}

// Load statistics
async function loadStatistics() {
    const days = document.getElementById('timeRange').value;

    try {
        const response = await fetch(`${API_BASE_URL}/database/attendance/summary/?days=${days}`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();

        if (data.success) {
            updateStatistics(data.data);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
        showToast('Lỗi khi tải thống kê', 'error');
    }
}

// Update statistics
function updateStatistics(stats) {
    document.getElementById('attendanceRate').textContent = stats.present_rate || '0%';
    document.getElementById('aiAccuracy').textContent = stats.avg_face_detection_confidence || '0%';
    document.getElementById('lateCount').textContent = stats.late_count || 0;
    document.getElementById('absentCount').textContent = stats.absent_count || 0;
}

// Filter activity
function filterActivity() {
    const searchTerm = document.getElementById('searchActivity').value.toLowerCase();
    const filterType = document.getElementById('filterActivity').value;
    const rows = document.querySelectorAll('#activityTable tr');

    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        const type = row.querySelector('td:nth-child(2)')?.textContent || '';

        const matchesSearch = text.includes(searchTerm);
        const matchesFilter = !filterType || type.includes(filterType);

        row.style.display = matchesSearch && matchesFilter ? '' : 'none';
    });
}

// Load teachers for select dropdown
async function loadTeachersForSelect() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/teachers/`, {
            headers: getAuthHeaders()
        });
        const data = await response.json();

        const select = document.getElementById('teacherSelect');
        select.innerHTML = '<option value="">Chọn giảng viên</option>';

        // Handle the API response format: {success: true, data: [...]}
        let teachers = [];
        if (data.success && data.data) {
            teachers = data.data;
        } else if (Array.isArray(data)) {
            teachers = data;
        }

        teachers.forEach(teacher => {
            const option = document.createElement('option');
            option.value = teacher.id;
            option.textContent = teacher.full_name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading teachers:', error);
    }
}

// Handle add student
async function handleAddStudent(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const studentData = {
        student_code: formData.get('student_code'),
        name: formData.get('name'),
        student_class: formData.get('student_class'),
        email: formData.get('email'),
        phone_number: formData.get('phone')
    };

    try {
        const response = await fetch(`${API_BASE_URL}/database/students/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(studentData)
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Thêm sinh viên thành công!', 'success');
            closeModal('addStudentModal');
            event.target.reset();
            loadDashboardData();
        } else {
            showToast(data.message || 'Lỗi khi thêm sinh viên', 'error');
        }
    } catch (error) {
        console.error('Error adding student:', error);
        showToast('Lỗi khi thêm sinh viên', 'error');
    }
}

// Handle add teacher
async function handleAddTeacher(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const teacherData = {
        username: formData.get('username'),
        full_name: formData.get('full_name'),
        email: formData.get('email'),
        phone_number: formData.get('phone'),
        password: formData.get('password'),
        role: 'teacher'
    };

    try {
        const response = await fetch(`${API_BASE_URL}/users/register/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(teacherData)
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Thêm giảng viên thành công!', 'success');
            closeModal('addTeacherModal');
            event.target.reset();
            loadDashboardData();
            loadTeachersForSelect();
        } else {
            showToast(data.message || 'Lỗi khi thêm giảng viên', 'error');
        }
    } catch (error) {
        console.error('Error adding teacher:', error);
        showToast('Lỗi khi thêm giảng viên', 'error');
    }
}

// Handle add subject
async function handleAddSubject(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const subjectData = {
        subject_name: formData.get('subject_name'),
        time: formData.get('time'),
        teacher: formData.get('teacher') || null,
        for_teacher: formData.get('for_teacher') === 'true'
    };

    try {
        const response = await fetch(`${API_BASE_URL}/database/subjects/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify(subjectData)
        });

        const data = await response.json();

        if (response.ok) {
            showToast('Thêm môn học thành công!', 'success');
            closeModal('addSubjectModal');
            event.target.reset();
            loadDashboardData();
        } else {
            showToast(data.message || 'Lỗi khi thêm môn học', 'error');
        }
    } catch (error) {
        console.error('Error adding subject:', error);
        showToast('Lỗi khi thêm môn học', 'error');
    }
}

// Start attendance
function startAttendance() {
    // Redirect to attendance page or open camera
    window.location.href = 'attendance.html';
}

// Refresh data
function refreshData() {
    loadDashboardData();
    loadRecentActivity();
    loadStatistics();
    showToast('Đã làm mới dữ liệu', 'success');
}

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Utility functions
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN');
}

function showToast(message, type = 'info') {
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast');
    existingToasts.forEach(toast => toast.remove());

    // Create new toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    document.body.appendChild(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
}

// Export functions for global access
window.openModal = openModal;
window.closeModal = closeModal;
window.refreshData = refreshData;
window.startAttendance = startAttendance; 