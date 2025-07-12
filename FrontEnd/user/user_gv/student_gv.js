// student_gv.js - Student management for teachers

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Global variables
let studentsData = [];
let attendanceData = [];
let currentEditingStudent = null;

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadStudents();
    loadAttendanceData();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search and filter functionality
    document.getElementById('searchStudent').addEventListener('input', filterStudents);
    document.getElementById('filterClass').addEventListener('change', filterStudents);
    document.getElementById('filterStatus').addEventListener('change', filterStudents);

    // Modal close on outside click
    window.addEventListener('click', function (event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Load students data
async function loadStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/database/students/`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        if (data.success) {
            studentsData = data.data;
            displayStudentsTable(studentsData);
            updateClassFilter();
            updateStatistics();
        } else {
            showToast('Lỗi khi tải dữ liệu sinh viên', 'error');
        }
    } catch (error) {
        console.error('Error loading students:', error);
        showToast('Lỗi khi tải dữ liệu sinh viên', 'error');
    }
}

// Load attendance data for today
async function loadAttendanceData() {
    try {
        const today = new Date().toISOString().split('T')[0];
        const response = await fetch(`${API_BASE_URL}/database/attendance/history/?date=${today}`, {
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        if (data.success) {
            attendanceData = data.data;
            updateStatistics();
        }
    } catch (error) {
        console.error('Error loading attendance data:', error);
    }
}

// Display students table
function displayStudentsTable(studentsToShow) {
    const tbody = document.getElementById('studentsTable');
    tbody.innerHTML = '';

    if (studentsToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align: center;">Không có dữ liệu sinh viên</td></tr>';
        return;
    }

    studentsToShow.forEach(student => {
        const row = document.createElement('tr');
        const statusClass = student.is_active ? 'status-active' : 'status-inactive';
        const statusText = student.is_active ? 'Hoạt động' : 'Không hoạt động';

        // Check if student attended today
        const todayAttendance = attendanceData.find(att =>
            att.student_code === student.student_code &&
            new Date(att.timestamp).toDateString() === new Date().toDateString()
        );
        const attendanceStatus = todayAttendance ?
            `<span class="status-badge status-active">Đã điểm danh</span>` :
            `<span class="status-badge status-inactive">Chưa điểm danh</span>`;

        row.innerHTML = `
            <td>${student.student_code}</td>
            <td>${student.full_name}</td>
            <td>${student.class_name || 'N/A'}</td>
            <td>${student.email || 'N/A'}</td>
            <td>${student.phone_number || 'N/A'}</td>
            <td><span class="status-badge ${statusClass}">${statusText}</span></td>
            <td>${attendanceStatus}</td>
            <td>
                <button class="btn btn-success btn-sm" onclick="viewStudentDetail(${student.id})" title="Xem chi tiết">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-primary btn-sm" onclick="editStudent(${student.id})" title="Sửa">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-danger btn-sm" onclick="deleteStudent(${student.id})" title="Xóa">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
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
    const statusFilter = document.getElementById('filterStatus').value;

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

    if (statusFilter) {
        const isActive = statusFilter === 'active';
        filtered = filtered.filter(student => student.is_active === isActive);
    }

    displayStudentsTable(filtered);
}

// Clear all filters
function clearFilters() {
    document.getElementById('searchStudent').value = '';
    document.getElementById('filterClass').value = '';
    document.getElementById('filterStatus').value = '';
    displayStudentsTable(studentsData);
}

// Update statistics
function updateStatistics() {
    const totalStudents = studentsData.length;
    const activeStudents = studentsData.filter(s => s.is_active).length;

    const todayAttendance = attendanceData.filter(att =>
        new Date(att.timestamp).toDateString() === new Date().toDateString()
    ).length;

    const absentToday = totalStudents - todayAttendance;
    const attendanceRate = totalStudents > 0 ? ((todayAttendance / totalStudents) * 100).toFixed(1) : 0;

    document.getElementById('totalStudents').textContent = totalStudents;
    document.getElementById('attendedToday').textContent = todayAttendance;
    document.getElementById('absentToday').textContent = absentToday;
    document.getElementById('attendanceRate').textContent = attendanceRate + '%';
}

// Open add student modal
function openAddStudentModal() {
    currentEditingStudent = null;
    document.getElementById('modalTitle').textContent = 'Thêm sinh viên mới';
    document.getElementById('studentForm').reset();
    openModal('studentModal');
}

// Edit student
function editStudent(studentId) {
    const student = studentsData.find(s => s.id === studentId);
    if (!student) return;

    currentEditingStudent = student;
    document.getElementById('modalTitle').textContent = 'Sửa thông tin sinh viên';

    // Fill form with student data
    document.getElementById('studentCode').value = student.student_code;
    document.getElementById('studentName').value = student.full_name;
    document.getElementById('studentClass').value = student.class_name || '';
    document.getElementById('studentEmail').value = student.email || '';
    document.getElementById('studentPhone').value = student.phone_number || '';
    document.getElementById('studentBirth').value = student.date_of_birth || '';
    document.getElementById('studentGender').value = student.gender || '';
    document.getElementById('studentAddress').value = student.address || '';
    document.getElementById('studentStatus').value = student.is_active ? 'active' : 'inactive';

    openModal('studentModal');
}

// Save student (create or update)
async function saveStudent(event) {
    event.preventDefault();

    const formData = {
        student_code: document.getElementById('studentCode').value,
        full_name: document.getElementById('studentName').value,
        class_name: document.getElementById('studentClass').value,
        email: document.getElementById('studentEmail').value,
        phone_number: document.getElementById('studentPhone').value,
        date_of_birth: document.getElementById('studentBirth').value,
        gender: document.getElementById('studentGender').value,
        address: document.getElementById('studentAddress').value,
        is_active: document.getElementById('studentStatus').value === 'active'
    };

    try {
        const url = currentEditingStudent ?
            `${API_BASE_URL}/database/students/${currentEditingStudent.id}/` :
            `${API_BASE_URL}/database/students/`;

        const method = currentEditingStudent ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            showToast(
                currentEditingStudent ? 'Cập nhật sinh viên thành công' : 'Thêm sinh viên thành công',
                'success'
            );
            closeModal('studentModal');
            loadStudents();
        } else {
            showToast(data.message || 'Lỗi khi lưu sinh viên', 'error');
        }
    } catch (error) {
        console.error('Error saving student:', error);
        showToast('Lỗi khi lưu sinh viên', 'error');
    }
}

// Delete student
function deleteStudent(studentId) {
    const student = studentsData.find(s => s.id === studentId);
    if (!student) return;

    document.getElementById('deleteStudentName').textContent = `${student.student_code} - ${student.full_name}`;
    currentEditingStudent = student;
    openModal('deleteModal');
}

// Confirm delete
async function confirmDelete() {
    if (!currentEditingStudent) return;

    try {
        const response = await fetch(`${API_BASE_URL}/database/students/${currentEditingStudent.id}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getAuthToken()}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            showToast('Xóa sinh viên thành công', 'success');
            closeModal('deleteModal');
            loadStudents();
        } else {
            showToast('Lỗi khi xóa sinh viên', 'error');
        }
    } catch (error) {
        console.error('Error deleting student:', error);
        showToast('Lỗi khi xóa sinh viên', 'error');
    }
}

// View student detail
function viewStudentDetail(studentId) {
    const student = studentsData.find(s => s.id === studentId);
    if (!student) return;

    // Show student detail in modal or redirect
    showToast(`Xem chi tiết sinh viên: ${student.full_name}`, 'info');
    // openStudentDetailModal(student);
}

// Export students to Excel
function exportStudents() {
    const filteredStudents = getFilteredStudents();

    // Create CSV content
    const headers = ['MSSV', 'Họ tên', 'Lớp', 'Email', 'Số điện thoại', 'Ngày sinh', 'Giới tính', 'Địa chỉ', 'Trạng thái'];
    const csvContent = [
        headers.join(','),
        ...filteredStudents.map(student => [
            student.student_code,
            student.full_name,
            student.class_name || 'N/A',
            student.email || 'N/A',
            student.phone_number || 'N/A',
            student.date_of_birth || 'N/A',
            student.gender || 'N/A',
            student.address || 'N/A',
            student.is_active ? 'Hoạt động' : 'Không hoạt động'
        ].join(','))
    ].join('\n');

    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `danh_sach_sinh_vien_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showToast('Đã xuất danh sách sinh viên', 'success');
}

// Get filtered students for export
function getFilteredStudents() {
    const searchTerm = document.getElementById('searchStudent').value.toLowerCase();
    const classFilter = document.getElementById('filterClass').value;
    const statusFilter = document.getElementById('filterStatus').value;

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

    if (statusFilter) {
        const isActive = statusFilter === 'active';
        filtered = filtered.filter(student => student.is_active === isActive);
    }

    return filtered;
}

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Utility functions
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
window.openAddStudentModal = openAddStudentModal;
window.editStudent = editStudent;
window.deleteStudent = deleteStudent;
window.saveStudent = saveStudent;
window.confirmDelete = confirmDelete;
window.viewStudentDetail = viewStudentDetail;
window.exportStudents = exportStudents;
window.clearFilters = clearFilters;
window.filterStudents = filterStudents;
window.openModal = openModal;
window.closeModal = closeModal; 