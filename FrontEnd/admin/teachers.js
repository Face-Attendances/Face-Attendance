// Global variables
let teachers = [];
let currentTeacherId = null;
let deleteTeacherId = null;

// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const TEACHERS_API = `${API_BASE_URL}/database/teachers/`;

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadTeachers();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    document.getElementById('searchTeacher').addEventListener('input', function () {
        filterTeachers();
    });

    // Department filter
    document.getElementById('departmentFilter').addEventListener('change', function () {
        filterTeachers();
    });

    // Form submission
    document.getElementById('teacherForm').addEventListener('submit', function (e) {
        e.preventDefault();
        saveTeacher();
    });
}

// Load teachers from API
async function loadTeachers() {
    try {
        // GET không cần gửi Authorization
        const response = await fetch(TEACHERS_API, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            teachers = data;
            displayTeachers();
            updateDepartmentFilter();
        } else {
            console.error('Failed to load teachers:', response.status);
            showNotification('Lỗi khi tải danh sách giảng viên', 'error');
        }
    } catch (error) {
        console.error('Error loading teachers:', error);
        showNotification('Lỗi kết nối khi tải giảng viên', 'error');
    }
}

// Display teachers in table
function displayTeachers() {
    const tbody = document.getElementById('teachersTable');
    tbody.innerHTML = '';

    teachers.forEach(teacher => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${teacher.teacher_code || ''}</td>
            <td>${teacher.name || ''}</td>
            <td>${teacher.department || ''}</td>
            <td>${teacher.email || ''}</td>
            <td>${teacher.phone_number || ''}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editTeacher(${teacher.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteTeacher(${teacher.id}, '${teacher.name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Filter teachers
function filterTeachers() {
    const searchTerm = document.getElementById('searchTeacher').value.toLowerCase();
    const departmentFilter = document.getElementById('departmentFilter').value;

    const filtered = teachers.filter(teacher => {
        const matchesSearch = !searchTerm ||
            (teacher.teacher_code && teacher.teacher_code.toLowerCase().includes(searchTerm)) ||
            (teacher.name && teacher.name.toLowerCase().includes(searchTerm));

        const matchesDepartment = !departmentFilter || teacher.department === departmentFilter;

        return matchesSearch && matchesDepartment;
    });

    displayFilteredTeachers(filtered);
}

// Display filtered teachers
function displayFilteredTeachers(filteredTeachers) {
    const tbody = document.getElementById('teachersTable');
    tbody.innerHTML = '';

    filteredTeachers.forEach(teacher => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${teacher.teacher_code || ''}</td>
            <td>${teacher.name || ''}</td>
            <td>${teacher.department || ''}</td>
            <td>${teacher.email || ''}</td>
            <td>${teacher.phone_number || ''}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editTeacher(${teacher.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteTeacher(${teacher.id}, '${teacher.name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update department filter options
function updateDepartmentFilter() {
    const select = document.getElementById('departmentFilter');
    const currentValue = select.value;

    select.innerHTML = '<option value="">Tất cả khoa</option>';

    const uniqueDepartments = [...new Set(teachers.map(t => t.department).filter(d => d))];
    uniqueDepartments.forEach(department => {
        const option = document.createElement('option');
        option.value = department;
        option.textContent = department;
        if (department === currentValue) {
            option.selected = true;
        }
        select.appendChild(option);
    });
}

// Open modal for adding new teacher
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
    if (modalId === 'addTeacherModal') {
        resetForm();
    }
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Reset form
function resetForm() {
    document.getElementById('teacherForm').reset();
    document.getElementById('teacherId').value = '';
    document.getElementById('teacherModalTitle').textContent = 'Thêm giảng viên mới';
    document.getElementById('teacherSubmitBtn').textContent = 'Thêm giảng viên';
    currentTeacherId = null;
}

// Edit teacher
function editTeacher(id) {
    const teacher = teachers.find(t => t.id === id);
    if (teacher) {
        currentTeacherId = id;
        document.getElementById('teacherId').value = teacher.id;
        document.getElementById('teacherCode').value = teacher.teacher_code || '';
        document.getElementById('teacherName').value = teacher.name || '';
        document.getElementById('teacherDepartment').value = teacher.department || '';
        document.getElementById('teacherDayofbirth').value = teacher.dayofbirth || '';
        document.getElementById('teacherEmail').value = teacher.email || '';
        document.getElementById('teacherPhone').value = teacher.phone_number || '';
        document.getElementById('teacherAddress').value = teacher.address || '';

        document.getElementById('teacherModalTitle').textContent = 'Chỉnh sửa giảng viên';
        document.getElementById('teacherSubmitBtn').textContent = 'Cập nhật giảng viên';

        openModal('addTeacherModal');
    }
}

// Save teacher (create or update)
async function saveTeacher() {
    const formData = new FormData(document.getElementById('teacherForm'));
    const teacherData = {
        teacher_code: formData.get('teacher_code'),
        name: formData.get('name'),
        department: formData.get('department'),
        dayofbirth: formData.get('dayofbirth'),
        email: formData.get('email'),
        phone_number: formData.get('phone_number'),
        address: formData.get('address')
    };

    // Log dữ liệu gửi lên để debug
    console.log('=== DEBUG: Teacher Data ===');
    console.log('Teacher data gửi lên:', teacherData);
    console.log('Current teacher ID:', currentTeacherId);
    console.log('Form data entries:');
    for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
    }

    try {
        const token = localStorage.getItem('accessToken');
        const url = currentTeacherId ? `${TEACHERS_API}${currentTeacherId}/` : `${TEACHERS_API}create/`;
        const method = currentTeacherId ? 'PUT' : 'POST';

        console.log('=== DEBUG: Request Info ===');
        console.log('URL:', url);
        console.log('Method:', method);
        console.log('Token exists:', !!token);

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(teacherData)
        });

        console.log('=== DEBUG: Response Info ===');
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);

        if (response.ok) {
            const result = await response.json();
            console.log('Success response:', result);
            showNotification(
                currentTeacherId ? 'Cập nhật giảng viên thành công!' : 'Thêm giảng viên thành công!',
                'success'
            );
            closeModal('addTeacherModal');
            loadTeachers();
        } else {
            let errorText = '';
            try {
                const error = await response.json();
                console.error('=== DEBUG: Error Response ===');
                console.error('Full error object:', error);
                console.error('Error keys:', Object.keys(error));

                // Xử lý các loại lỗi cụ thể
                if (error.teacher_code) {
                    errorText = `Mã giảng viên đã tồn tại hoặc không hợp lệ: ${error.teacher_code.join(', ')}`;
                } else if (error.email) {
                    errorText = `Email đã tồn tại hoặc không hợp lệ: ${error.email.join(', ')}`;
                } else if (error.name) {
                    errorText = `Tên không hợp lệ: ${error.name.join(', ')}`;
                } else if (error.dayofbirth) {
                    errorText = `Ngày sinh không hợp lệ: ${error.dayofbirth.join(', ')}`;
                } else if (error.error) {
                    errorText = `Lỗi: ${error.error}`;
                } else {
                    errorText = `Lỗi không xác định: ${JSON.stringify(error)}`;
                }
            } catch (e) {
                errorText = 'Lỗi không đọc được phản hồi từ server.';
                console.error('Error parsing error response:', e);
            }

            console.error('Final error message:', errorText);
            showNotification(errorText, 'error');
        }
    } catch (error) {
        console.error('=== DEBUG: Network Error ===');
        console.error('Network error:', error);
        showNotification('Lỗi kết nối khi lưu giảng viên', 'error');
    }
}

// Delete teacher
function deleteTeacher(id, name) {
    deleteTeacherId = id;
    document.getElementById('deleteTeacherName').textContent = name;
    openModal('deleteModal');
}

// Confirm delete
async function confirmDelete() {
    if (!deleteTeacherId) return;

    try {
        const token = localStorage.getItem('accessToken');
        const response = await fetch(`${TEACHERS_API}${deleteTeacherId}/delete/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            showNotification('Xóa giảng viên thành công!', 'success');
            closeModal('deleteModal');
            loadTeachers();
        } else {
            console.error('Failed to delete teacher:', response.status);
            showNotification('Lỗi khi xóa giảng viên', 'error');
        }
    } catch (error) {
        console.error('Error deleting teacher:', error);
        showNotification('Lỗi kết nối khi xóa giảng viên', 'error');
    }
}

// View teacher details
function viewTeacherDetails(teacherId) {
    const teacher = teachers.find(t => t.id === teacherId);
    if (!teacher) return;

    alert(`Teacher Details:\nCode: ${teacher.teacher_code}\nName: ${teacher.name}\nDepartment: ${teacher.department || 'N/A'}\nEmail: ${teacher.email || 'N/A'}\nPhone: ${teacher.phone_number || 'N/A'}\nAddress: ${teacher.address || 'N/A'}`);
}

// Export teachers to Excel
function exportTeachers() {
    // Implementation for Excel export
    showNotification('Tính năng xuất Excel đang được phát triển', 'info');
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    // Add to page
    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Close modals when clicking outside
window.onclick = function (event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
} 