// students.js - Student management functionality

// API Base URL
const API_BASE_URL = 'http://localhost:8000/api';

// Global variables
let students = [];
let currentStudentId = null;
let isEditMode = false;

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadStudents();
    setupEventListeners();
    loadClasses();
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    document.getElementById('searchStudent').addEventListener('input', filterStudents);
    document.getElementById('filterClass').addEventListener('change', filterStudents);

    // Form submission
    document.getElementById('studentForm').addEventListener('submit', handleStudentSubmit);

    // Modal close on outside click
    window.addEventListener('click', function (event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Load students
async function loadStudents() {
    try {
        const response = await fetch(`${API_BASE_URL}/database/students/`);
        const data = await response.json();

        if (response.ok) {
            students = data;
            displayStudents(students);
            updateClassFilter();
        } else {
            showToast('Lỗi khi tải danh sách sinh viên', 'error');
        }
    } catch (error) {
        console.error('Error loading students:', error);
        showToast('Lỗi khi tải danh sách sinh viên', 'error');
    }
}

// Display students in table
function displayStudents(studentsToShow) {
    const tbody = document.getElementById('studentsTable');
    tbody.innerHTML = '';

    if (studentsToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center;">Không có sinh viên nào</td></tr>';
        return;
    }

    studentsToShow.forEach(student => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${student.student_code}</td>
            <td>${student.name}</td>
            <td>${student.student_class}</td>
            <td>${student.email || '-'}</td>
            <td>${student.phone_number || '-'}</td>
            <td><span class="status-badge status-active">Hoạt động</span></td>
            <td>
                <button class="btn btn-warning btn-sm" onclick="editStudent(${student.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-danger btn-sm" onclick="deleteStudent(${student.id}, '${student.name}')">
                    <i class="fas fa-trash"></i>
                </button>
                <button class="btn btn-success btn-sm" onclick="viewStudentDetails(${student.id})">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Filter students
function filterStudents() {
    const searchTerm = document.getElementById('searchStudent').value.toLowerCase();
    const selectedClass = document.getElementById('filterClass').value;

    const filtered = students.filter(student => {
        const matchesSearch =
            student.student_code.toLowerCase().includes(searchTerm) ||
            student.name.toLowerCase().includes(searchTerm) ||
            (student.student_class && student.student_class.toLowerCase().includes(searchTerm));

        const matchesClass = !selectedClass || student.student_class === selectedClass;

        return matchesSearch && matchesClass;
    });

    displayStudents(filtered);
}

// Update class filter dropdown
function updateClassFilter() {
    const classes = [...new Set(students.map(s => s.student_class).filter(Boolean))];
    const select = document.getElementById('filterClass');

    // Keep the "Tất cả lớp" option
    select.innerHTML = '<option value="">Tất cả lớp</option>';

    classes.forEach(className => {
        const option = document.createElement('option');
        option.value = className;
        option.textContent = className;
        select.appendChild(option);
    });
}

// Load classes for filter
function loadClasses() {
    // This will be populated when students are loaded
}

// Handle student form submission
async function handleStudentSubmit(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const studentData = {
        student_code: formData.get('student_code'),
        name: formData.get('name'),
        student_class: formData.get('student_class'),
        dayofbirth: formData.get('dayofbirth'),
        email: formData.get('email'),
        phone_number: formData.get('phone'),
        address: formData.get('address')
    };

    try {
        const url = isEditMode
            ? `${API_BASE_URL}/database/students/${currentStudentId}/update/`
            : `${API_BASE_URL}/database/students/create/`;

        const method = isEditMode ? 'PUT' : 'POST';

        const response = await window.authHelper.makeAuthenticatedRequest(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(studentData)
        });

        if (response) {
            const data = await response.json();

            if (response.ok) {
                showToast(
                    isEditMode ? 'Cập nhật sinh viên thành công!' : 'Thêm sinh viên thành công!',
                    'success'
                );
                closeModal('addStudentModal');
                resetForm();
                loadStudents();
            } else {
                showToast(data.message || 'Lỗi khi lưu sinh viên', 'error');
            }
        } else {
            showToast('Lỗi xác thực, vui lòng đăng nhập lại', 'error');
        }
    } catch (error) {
        console.error('Error saving student:', error);
        showToast('Lỗi khi lưu sinh viên', 'error');
    }
}

// Edit student
function editStudent(studentId) {
    const student = students.find(s => s.id === studentId);
    if (!student) return;

    isEditMode = true;
    currentStudentId = studentId;

    // Fill form with student data
    document.getElementById('studentId').value = student.id;
    document.getElementById('studentCode').value = student.student_code;
    document.getElementById('studentName').value = student.name;
    document.getElementById('studentClass').value = student.student_class;
    document.getElementById('studentDayofbirth').value = student.dayofbirth || '';
    document.getElementById('studentEmail').value = student.email || '';
    document.getElementById('studentPhone').value = student.phone_number || '';
    document.getElementById('studentAddress').value = student.address || '';

    // Update modal title and button
    document.getElementById('studentModalTitle').textContent = 'Chỉnh sửa sinh viên';
    document.getElementById('studentSubmitBtn').textContent = 'Cập nhật sinh viên';

    openModal('addStudentModal');
}

// Delete student
function deleteStudent(studentId, studentName) {
    currentStudentId = studentId;
    document.getElementById('deleteStudentName').textContent = studentName;
    openModal('deleteModal');
}

// Confirm delete
async function confirmDelete() {
    try {
        const response = await window.authHelper.makeAuthenticatedRequest(`${API_BASE_URL}/database/students/${currentStudentId}/delete/`, {
            method: 'DELETE'
        });

        if (response && response.ok) {
            showToast('Xóa sinh viên thành công!', 'success');
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

// View student details
function viewStudentDetails(studentId) {
    const student = students.find(s => s.id === studentId);
    if (!student) return;

    // You can implement a detailed view modal here
    alert(`Chi tiết sinh viên:\nMã SV: ${student.student_code}\nTên: ${student.name}\nLớp: ${student.student_class}\nEmail: ${student.email || 'N/A'}\nSĐT: ${student.phone_number || 'N/A'}`);
}

// Export students to Excel
function exportStudents() {
    // Create CSV content
    const headers = ['Mã SV', 'Họ và tên', 'Lớp', 'Email', 'Số điện thoại', 'Địa chỉ'];
    const csvContent = [
        headers.join(','),
        ...students.map(student => [
            student.student_code,
            student.name,
            student.student_class,
            student.email || '',
            student.phone_number || '',
            student.address || ''
        ].join(','))
    ].join('\n');

    // Create and download file
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

// Reset form
function resetForm() {
    document.getElementById('studentForm').reset();
    document.getElementById('studentId').value = '';
    isEditMode = false;
    currentStudentId = null;
    document.getElementById('studentModalTitle').textContent = 'Thêm sinh viên mới';
    document.getElementById('studentSubmitBtn').textContent = 'Thêm sinh viên';
}

// Modal functions
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
    if (modalId === 'addStudentModal') {
        resetForm();
    }
}

// Utility functions
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
window.editStudent = editStudent;
window.deleteStudent = deleteStudent;
window.viewStudentDetails = viewStudentDetails;
window.confirmDelete = confirmDelete;
window.exportStudents = exportStudents; 