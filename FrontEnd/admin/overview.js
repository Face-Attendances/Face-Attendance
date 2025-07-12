// overview.js - Dashboard functionality

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Global variables
let currentUser = null;
let dashboardData = {};

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
    try {
        const response = await fetch(`${API_BASE_URL}/database/attendance/summary/`);
        const data = await response.json();

        if (data.success) {
            dashboardData = data.data;
            updateDashboardCards();
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Lỗi khi tải dữ liệu dashboard', 'error');
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
        const response = await fetch(`${API_BASE_URL}/database/attendance/history/?days=7`);
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
        const response = await fetch(`${API_BASE_URL}/database/attendance/summary/?days=${days}`);
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
        const response = await fetch(`${API_BASE_URL}/users/teachers/`);
        const data = await response.json();

        const select = document.getElementById('teacherSelect');
        select.innerHTML = '<option value="">Chọn giảng viên</option>';

        data.forEach(teacher => {
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
            headers: {
                'Content-Type': 'application/json',
            },
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
            headers: {
                'Content-Type': 'application/json',
            },
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
            headers: {
                'Content-Type': 'application/json',
            },
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