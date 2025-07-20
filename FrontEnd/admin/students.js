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
    updateStatistics();
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
            updateStatistics();
        } else {
            showToast('Lỗi khi tải danh sách sinh viên', 'error');
        }
    } catch (error) {
        console.error('Error loading students:', error);
        showToast('Lỗi khi tải danh sách sinh viên', 'error');
    }
}

// Update statistics
function updateStatistics() {
    const totalStudents = students.length;
    const activeStudents = students.filter(s => s.is_active !== false).length;
    const uniqueClasses = [...new Set(students.map(s => s.student_class).filter(Boolean))].length;
    const newStudents = students.filter(s => {
        const createdDate = new Date(s.created_at || Date.now());
        const oneMonthAgo = new Date();
        oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1);
        return createdDate > oneMonthAgo;
    }).length;

    document.getElementById('totalStudents').textContent = totalStudents;
    document.getElementById('activeStudents').textContent = activeStudents;
    document.getElementById('totalClasses').textContent = uniqueClasses;
    document.getElementById('newStudents').textContent = newStudents;
}

// Display students in table
function displayStudents(studentsToShow) {
    const tbody = document.getElementById('studentsTable');
    tbody.innerHTML = '';

    if (studentsToShow.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 40px; color: #718096;">
                    <i class="fas fa-search" style="font-size: 2rem; margin-bottom: 16px; display: block; color: #a0aec0;"></i>
                    Không tìm thấy sinh viên nào
                </td>
            </tr>
        `;
        return;
    }

    studentsToShow.forEach(student => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="student-code">${student.student_code}</span></td>
            <td><span class="student-name">${student.name}</span></td>
            <td><span class="student-class">${student.student_class}</span></td>
            <td>${student.email || '-'}</td>
            <td>${student.phone_number || '-'}</td>
            <td><span class="status-badge status-active">Hoạt động</span></td>
            <td>
                <div class="table-actions">
                    <button class="btn btn-warning btn-icon" onclick="editStudent(${student.id})" title="Chỉnh sửa">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-danger btn-icon" onclick="deleteStudent(${student.id}, '${student.name}')" title="Xóa">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button class="btn btn-success btn-icon" onclick="viewStudentDetails(${student.id})" title="Xem chi tiết">
                        <i class="fas fa-eye"></i>
                    </button>
                </div>
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

    const token = localStorage.getItem('accessToken'); // Lấy token
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
        let url, method;
        if (isEditMode) {
            const student = students.find(s => s.id === currentStudentId);
            if (!student) {
                showToast('Không tìm thấy sinh viên để cập nhật', 'error');
                return;
            }
            url = `${API_BASE_URL}/database/students/${student.student_code}/update/`;
            method = 'PUT';
        } else {
            url = `${API_BASE_URL}/database/students/create/`;
            method = 'POST';
        }

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token // Thêm Authorization header
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
    if (!currentStudentId) {
        showToast('Không có sinh viên nào được chọn để xóa', 'error');
        return;
    }

    try {
        const token = localStorage.getItem('accessToken'); // Lấy token
        const student = students.find(s => s.id === currentStudentId);
        if (!student) {
            showToast('Không tìm thấy sinh viên để xóa', 'error');
            return;
        }
        console.log('🗑️ Deleting student ID:', currentStudentId);

        const response = await fetch(`${API_BASE_URL}/database/students/${student.student_code}/delete/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token // Thêm Authorization header
            }
        });

        console.log('Delete response status:', response.status);
        console.log('Delete response ok:', response.ok);

        if (response.ok) {
            // Handle both 200 and 204 status codes as success
            if (response.status === 204 || response.status === 200) {
                showToast('Xóa sinh viên thành công!', 'success');
                closeModal('deleteModal');
                currentStudentId = null; // Reset
                await loadStudents(); // Reload data
            } else {
                const errorData = await response.json();
                showToast('Lỗi khi xóa: ' + (errorData.message || 'Unknown error'), 'error');
            }
        } else {
            let errorMessage = 'Lỗi khi xóa sinh viên';
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorData.error || errorMessage;
            } catch (e) {
                console.log('Could not parse error response');
            }
            showToast(errorMessage, 'error');
        }
    } catch (error) {
        console.error('Network error deleting student:', error);
        showToast('Lỗi kết nối khi xóa sinh viên: ' + error.message, 'error');
    }
}

// View student details
function viewStudentDetails(studentId) {
    const student = students.find(s => s.id === studentId);
    if (!student) return;

    // Create a detailed modal for student information
    const modalContent = `
        <div class="modal-content" style="max-width: 600px;">
            <div class="modal-header">
                <h3>Chi tiết sinh viên</h3>
                <span class="close" onclick="closeModal('detailsModal')">&times;</span>
            </div>
            <div style="padding: 24px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;">
                    <div>
                        <label style="font-weight: 600; color: #718096; font-size: 0.875rem;">Mã sinh viên</label>
                        <p style="margin: 8px 0; font-size: 1.125rem; color: #2d3748;">${student.student_code}</p>
                    </div>
                    <div>
                        <label style="font-weight: 600; color: #718096; font-size: 0.875rem;">Họ và tên</label>
                        <p style="margin: 8px 0; font-size: 1.125rem; color: #2d3748;">${student.name}</p>
                    </div>
                    <div>
                        <label style="font-weight: 600; color: #718096; font-size: 0.875rem;">Lớp</label>
                        <p style="margin: 8px 0; font-size: 1.125rem; color: #2d3748;">${student.student_class || 'N/A'}</p>
                    </div>
                    <div>
                        <label style="font-weight: 600; color: #718096; font-size: 0.875rem;">Ngày sinh</label>
                        <p style="margin: 8px 0; font-size: 1.125rem; color: #2d3748;">${student.dayofbirth || 'N/A'}</p>
                    </div>
                    <div>
                        <label style="font-weight: 600; color: #718096; font-size: 0.875rem;">Email</label>
                        <p style="margin: 8px 0; font-size: 1.125rem; color: #2d3748;">${student.email || 'N/A'}</p>
                    </div>
                    <div>
                        <label style="font-weight: 600; color: #718096; font-size: 0.875rem;">Số điện thoại</label>
                        <p style="margin: 8px 0; font-size: 1.125rem; color: #2d3748;">${student.phone_number || 'N/A'}</p>
                    </div>
                </div>
                <div>
                    <label style="font-weight: 600; color: #718096; font-size: 0.875rem;">Địa chỉ</label>
                    <p style="margin: 8px 0; font-size: 1.125rem; color: #2d3748;">${student.address || 'N/A'}</p>
                </div>
            </div>
        </div>
    `;

    // Create modal if it doesn't exist
    let modal = document.getElementById('detailsModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'detailsModal';
        modal.className = 'modal';
        document.body.appendChild(modal);
    }

    modal.innerHTML = modalContent;
    modal.style.display = 'block';
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