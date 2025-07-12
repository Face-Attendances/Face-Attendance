// user_gv.js - Teacher dashboard

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Global variables
let currentUser = null;
let studentsData = [];
let subjectsData = [];
let attendanceData = [];

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadDashboardData();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    document.getElementById('searchStudent').addEventListener('input', filterStudents);
    document.getElementById('filterClass').addEventListener('change', filterStudents);
}

// Load all dashboard data
async function loadDashboardData() {
    try {
        await Promise.all([
            loadUserInfo(),
            loadStudents(),
            loadSubjects(),
            loadRecentAttendance(),
            loadStatistics()
        ]);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showToast('Lỗi khi tải dữ liệu dashboard', 'error');
    }
}

// Load user information
async function loadUserInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/user/`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        if (data.success) {
            currentUser = data.user;
        }
    } catch (error) {
        console.error('Error loading user info:', error);
    }
}

// Load students data
async function loadStudents() {
    try {
        // GET không cần gửi Authorization
        const response = await fetch(`${API_BASE_URL}/database/students/`, {
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        if (data.success) {
            studentsData = data.data;
            displayStudentsTable(studentsData.slice(0, 10)); // Show first 10 students
            updateClassFilter();
        }
    } catch (error) {
        console.error('Error loading students:', error);
    }
}

// Load subjects data
async function loadSubjects() {
    try {
        // GET không cần gửi Authorization
        const response = await fetch(`${API_BASE_URL}/database/subjects/`, {
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const subjects = await response.json();

        // Filter subjects for current teacher
        if (currentUser && currentUser.role === 'teacher') {
            subjectsData = subjects.filter(subject =>
                subject.teacher === currentUser.id || subject.teacher_name === currentUser.full_name
            );
        } else {
            subjectsData = subjects;
        }

        displayTeachingSubjects();
    } catch (error) {
        console.error('Error loading subjects:', error);
    }
}

// Load recent attendance
async function loadRecentAttendance() {
    try {
        const response = await fetch(`${API_BASE_URL}/database/attendance/history/`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        if (data.success) {
            attendanceData = data.data;
            displayRecentAttendance(attendanceData.slice(0, 10)); // Show first 10 records
        }
    } catch (error) {
        console.error('Error loading attendance:', error);
    }
}

// Load statistics
async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/database/attendance/statistics/`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        if (data.success) {
            updateDashboardStats(data.stats);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Display teaching subjects
function displayTeachingSubjects() {
    const grid = document.getElementById('teachingSubjectsGrid');
    grid.innerHTML = '';

    if (subjectsData.length === 0) {
        grid.innerHTML = '<div class="no-data">Không có môn học nào</div>';
        return;
    }

    subjectsData.slice(0, 4).forEach(subject => {
        const card = document.createElement('div');
        card.className = 'dashboard-card';
        card.innerHTML = `
            <div class="card-header">
                <div class="card-icon subjects">
                    <i class="fas fa-book"></i>
                </div>
                <div>
                    <div class="card-title">${subject.subject_name}</div>
                    <div class="card-value">${subject.student_count || 0} sinh viên</div>
                </div>
            </div>
            <div class="card-footer">
                <small>Mã môn: ${subject.subject_code}</small>
            </div>
        `;
        grid.appendChild(card);
    });
}

// Display students table
function displayStudentsTable(studentsToShow) {
    const tbody = document.getElementById('studentsTable');
    tbody.innerHTML = '';

    if (studentsToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Không có dữ liệu sinh viên</td></tr>';
        return;
    }

    studentsToShow.forEach(student => {
        const row = document.createElement('tr');
        const statusClass = student.is_active ? 'status-active' : 'status-inactive';
        const statusText = student.is_active ? 'Hoạt động' : 'Không hoạt động';

        row.innerHTML = `
            <td>${student.student_code}</td>
            <td>${student.full_name}</td>
            <td>${student.class_name || 'N/A'}</td>
            <td>${student.email || 'N/A'}</td>
            <td>${student.phone_number || 'N/A'}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td>
                <button class="btn btn-success btn-sm" onclick="viewStudentDetail(${student.id})">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Display recent attendance
function displayRecentAttendance(attendanceToShow) {
    const tbody = document.getElementById('recentAttendanceTable');
    tbody.innerHTML = '';

    if (attendanceToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">Không có dữ liệu điểm danh gần đây</td></tr>';
        return;
    }

    attendanceToShow.forEach(record => {
        const row = document.createElement('tr');
        const statusClass = record.status === 'present' ? 'status-active' : 'status-inactive';
        const statusText = record.status === 'present' ? 'Có mặt' : 'Vắng mặt';

        row.innerHTML = `
            <td>${formatDateTime(record.timestamp)}</td>
            <td>${record.student_code}</td>
            <td>${record.student_name}</td>
            <td>${record.subject}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td>${record.face_detection_confidence ? record.face_detection_confidence.toFixed(1) + '%' : 'N/A'}</td>
        `;
        tbody.appendChild(row);
    });
}

// Update dashboard statistics
function updateDashboardStats(stats) {
    document.getElementById('totalStudents').textContent = stats.total_students || 0;
    document.getElementById('totalSubjects').textContent = stats.total_subjects || 0;
    document.getElementById('todayAttendance').textContent = stats.today_attendance || 0;
    document.getElementById('attendanceRate').textContent = (stats.attendance_rate || 0) + '%';

    // Cập nhật thông tin chi tiết nếu có
    if (stats.subject_stats) {
        console.log('Subject statistics:', stats.subject_stats);
    }
}

// Update class filter dropdown
function updateClassFilter() {
    const select = document.getElementById('filterClass');
    const classes = [...new Set(studentsData.map(student => student.class_name).filter(Boolean))];

    select.innerHTML = '<option value="">Tất cả lớp</option>';
    classes.forEach(className => {
        const option = document.createElement('option');
        option.value = className;
        option.textContent = className;
        select.appendChild(option);
    });
}

// Filter students
function filterStudents() {
    const searchTerm = document.getElementById('searchStudent').value.toLowerCase();
    const classFilter = document.getElementById('filterClass').value;

    let filtered = studentsData;

    if (searchTerm) {
        filtered = filtered.filter(student =>
            student.student_code.toLowerCase().includes(searchTerm) ||
            student.full_name.toLowerCase().includes(searchTerm) ||
            (student.email && student.email.toLowerCase().includes(searchTerm))
        );
    }

    if (classFilter) {
        filtered = filtered.filter(student => student.class_name === classFilter);
    }

    displayStudentsTable(filtered.slice(0, 10));
}

// Quick action functions
function startAttendance() {
    // Redirect to attendance page or open camera
    showToast('Chức năng điểm danh sẽ được mở', 'info');
    // window.location.href = '../attendance/attendance.html';
}

function viewAllSubjects() {
    // Redirect to subjects management page
    showToast('Chuyển đến trang quản lý môn học', 'info');
    // window.location.href = 'subjects_gv.html';
}

function exportReport() {
    // Export current data to Excel
    const dataToExport = {
        students: studentsData,
        subjects: subjectsData,
        attendance: attendanceData
    };

    // Create CSV content
    const headers = ['Loại', 'Mã', 'Tên', 'Thông tin bổ sung'];
    const csvContent = [
        headers.join(','),
        ...studentsData.map(student => [
            'Sinh viên',
            student.student_code,
            student.full_name,
            student.class_name || 'N/A'
        ].join(',')),
        ...subjectsData.map(subject => [
            'Môn học',
            subject.subject_code,
            subject.subject_name,
            subject.teacher_name || 'N/A'
        ].join(','))
    ].join('\n');

    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `bao_cao_giang_vien_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast('Đã xuất báo cáo', 'success');
}

function refreshData() {
    loadDashboardData();
    showToast('Đã làm mới dữ liệu', 'success');
}

// View student detail
function viewStudentDetail(studentId) {
    const student = studentsData.find(s => s.id === studentId);
    if (!student) return;

    // Show student detail in modal or redirect
    showToast(`Xem chi tiết sinh viên: ${student.full_name}`, 'info');
    // openStudentDetailModal(student);
}

// Utility functions
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function getAuthToken() {
    return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
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
window.startAttendance = startAttendance;
window.viewAllSubjects = viewAllSubjects;
window.exportReport = exportReport;
window.refreshData = refreshData;
window.viewStudentDetail = viewStudentDetail;
window.filterStudents = filterStudents; 