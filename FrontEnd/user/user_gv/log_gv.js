// log_gv.js - Attendance log for teachers

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Global variables
let attendanceData = [];
let teachingSubjects = [];
let currentUser = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadAttendanceData();
    loadTeachingSubjects();
    setupEventListeners();
    setDefaultDate();
});

// Setup event listeners
function setupEventListeners() {
    // Modal close on outside click
    window.addEventListener('click', function (event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Set default date to today
function setDefaultDate() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('dateFilter').value = today;
}

// Load attendance data for teacher's subjects
async function loadAttendanceData() {
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
            currentUser = data.user;
            displayAttendanceTable(attendanceData);
            updateStatistics(data.stats);
        } else {
            showToast('Lỗi khi tải dữ liệu điểm danh', 'error');
        }
    } catch (error) {
        console.error('Error loading attendance data:', error);
        showToast('Lỗi khi tải dữ liệu điểm danh', 'error');
    }
}

// Load teaching subjects for filter
async function loadTeachingSubjects() {
    try {
        const response = await fetch(`${API_BASE_URL}/database/subjects/`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });

        const subjects = await response.json();

        // Filter subjects that the current teacher is teaching
        if (currentUser && currentUser.role === 'teacher') {
            teachingSubjects = subjects.filter(subject =>
                subject.teacher === currentUser.id || subject.teacher_name === currentUser.full_name
            );
        } else {
            teachingSubjects = subjects; // For admin or if no teacher filter
        }

        updateSubjectFilter();
    } catch (error) {
        console.error('Error loading subjects:', error);
    }
}

// Update subject filter dropdown
function updateSubjectFilter() {
    const select = document.getElementById('subjectFilter');
    select.innerHTML = '<option value="">Tất cả môn học</option>';

    teachingSubjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject.subject_name;
        option.textContent = subject.subject_name;
        select.appendChild(option);
    });
}

// Display attendance table
function displayAttendanceTable(attendanceToShow) {
    const tbody = document.getElementById('attendanceTable');
    tbody.innerHTML = '';

    if (attendanceToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">Không có dữ liệu điểm danh</td></tr>';
        return;
    }

    attendanceToShow.forEach((record, index) => {
        const row = document.createElement('tr');
        const statusClass = record.status === 'present' ? 'status-active' : 'status-inactive';
        const statusText = record.status === 'present' ? 'Có mặt' : 'Vắng mặt';

        row.innerHTML = `
            <td>${index + 1}</td>
            <td>${formatDate(record.timestamp)}</td>
            <td>${record.student_code}</td>
            <td>${record.student_name}</td>
            <td>${record.subject}</td>
            <td>${formatTime(record.timestamp)}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td>${record.face_detection_confidence ? record.face_detection_confidence.toFixed(1) + '%' : 'N/A'}</td>
            <td>
                <button class="btn btn-success btn-sm" onclick="viewAttendanceDetail(${record.id})">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Filter attendance data
function filterAttendance() {
    const dateFilter = document.getElementById('dateFilter').value;
    const subjectFilter = document.getElementById('subjectFilter').value;
    const searchTerm = document.getElementById('searchAttendance').value.toLowerCase();

    let filtered = attendanceData;

    // Filter by date
    if (dateFilter) {
        const filterDate = new Date(dateFilter).toDateString();
        filtered = filtered.filter(record => {
            const recordDate = new Date(record.timestamp).toDateString();
            return recordDate === filterDate;
        });
    }

    // Filter by subject
    if (subjectFilter) {
        filtered = filtered.filter(record =>
            record.subject === subjectFilter
        );
    }

    // Filter by search term
    if (searchTerm) {
        filtered = filtered.filter(record =>
            record.student_code.toLowerCase().includes(searchTerm) ||
            record.student_name.toLowerCase().includes(searchTerm)
        );
    }

    displayAttendanceTable(filtered);
    updateFilteredStatistics(filtered);
}

// Update statistics based on filtered data
function updateFilteredStatistics(filteredData) {
    const total = filteredData.length;
    const present = filteredData.filter(record => record.status === 'present').length;
    const absent = filteredData.filter(record => record.status === 'absent').length;
    const rate = total > 0 ? ((present / total) * 100).toFixed(1) : 0;

    document.getElementById('totalAttendance').textContent = total;
    document.getElementById('presentCount').textContent = present;
    document.getElementById('absentCount').textContent = absent;
    document.getElementById('attendanceRate').textContent = rate + '%';
}

// Update statistics
function updateStatistics(stats) {
    document.getElementById('totalAttendance').textContent = stats.total_records || 0;
    document.getElementById('presentCount').textContent = stats.present_count || 0;
    document.getElementById('absentCount').textContent = stats.absent_count || 0;
    document.getElementById('attendanceRate').textContent = (stats.present_rate || 0) + '%';
}

// View attendance detail
async function viewAttendanceDetail(attendanceId) {
    try {
        const record = attendanceData.find(r => r.id === attendanceId);
        if (!record) return;

        const detailContent = document.getElementById('attendanceDetailContent');
        detailContent.innerHTML = `
            <div class="form-group">
                <label class="form-label"><strong>Thông tin sinh viên:</strong></label>
                <p>Mã SV: ${record.student_code}</p>
                <p>Họ tên: ${record.student_name}</p>
                <p>Lớp: ${record.student_class || 'N/A'}</p>
            </div>
            <div class="form-group">
                <label class="form-label"><strong>Thông tin điểm danh:</strong></label>
                <p>Môn học: ${record.subject}</p>
                <p>Ngày: ${formatDate(record.timestamp)}</p>
                <p>Giờ: ${formatTime(record.timestamp)}</p>
                <p>Trạng thái: <span class="status-badge ${record.status === 'present' ? 'status-active' : 'status-inactive'}">${record.status === 'present' ? 'Có mặt' : 'Vắng mặt'}</span></p>
                <p>Độ chính xác AI: ${record.face_detection_confidence ? record.face_detection_confidence.toFixed(1) + '%' : 'N/A'}</p>
                <p>Người thực hiện: ${record.detected_by_name || 'Hệ thống'}</p>
            </div>
            ${record.image_path ? `
            <div class="form-group">
                <label class="form-label"><strong>Ảnh điểm danh:</strong></label>
                <img src="${record.image_path}" alt="Ảnh điểm danh" style="max-width: 100%; height: auto; border-radius: 8px;">
            </div>
            ` : ''}
            ${record.notes ? `
            <div class="form-group">
                <label class="form-label"><strong>Ghi chú:</strong></label>
                <p>${record.notes}</p>
            </div>
            ` : ''}
        `;

        openModal('attendanceDetailModal');
    } catch (error) {
        console.error('Error loading attendance detail:', error);
        showToast('Lỗi khi tải chi tiết điểm danh', 'error');
    }
}

// Export attendance data to Excel
function exportAttendance() {
    const dateFilter = document.getElementById('dateFilter').value;
    const subjectFilter = document.getElementById('subjectFilter').value;

    let dataToExport = attendanceData;

    // Apply current filters
    if (dateFilter) {
        const filterDate = new Date(dateFilter).toDateString();
        dataToExport = dataToExport.filter(record => {
            const recordDate = new Date(record.timestamp).toDateString();
            return recordDate === filterDate;
        });
    }

    if (subjectFilter) {
        dataToExport = dataToExport.filter(record => record.subject === subjectFilter);
    }

    // Create CSV content
    const headers = ['STT', 'Ngày', 'MSSV', 'Họ tên', 'Môn học', 'Giờ điểm danh', 'Trạng thái', 'Độ chính xác AI', 'Người thực hiện'];
    const csvContent = [
        headers.join(','),
        ...dataToExport.map((record, index) => [
            index + 1,
            formatDate(record.timestamp),
            record.student_code,
            record.student_name,
            record.subject,
            formatTime(record.timestamp),
            record.status === 'present' ? 'Có mặt' : 'Vắng mặt',
            record.face_detection_confidence ? record.face_detection_confidence.toFixed(1) + '%' : 'N/A',
            record.detected_by_name || 'Hệ thống'
        ].join(','))
    ].join('\n');

    // Create and download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `nhat_ky_diem_danh_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast('Đã xuất nhật ký điểm danh', 'success');
}

// Refresh data
function refreshData() {
    loadAttendanceData();
    loadTeachingSubjects();
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
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
}

function getAuthToken() {
    // Get token from localStorage or sessionStorage
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
window.refreshData = refreshData;
window.filterAttendance = filterAttendance;
window.viewAttendanceDetail = viewAttendanceDetail;
window.exportAttendance = exportAttendance;
window.openModal = openModal;
window.closeModal = closeModal; 