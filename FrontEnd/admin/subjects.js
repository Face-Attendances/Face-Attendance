// Global variables
let subjects = [];
let teachers = [];
let currentSubjectId = null;
let deleteSubjectId = null;

// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const SUBJECTS_API = `${API_BASE_URL}/database/subjects/`;
const TEACHERS_API = `${API_BASE_URL}/database/teachers/`;

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadSubjects();
    loadTeachers();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    document.getElementById('searchSubject').addEventListener('input', function () {
        filterSubjects();
    });

    // Teacher filter
    document.getElementById('filterTeacher').addEventListener('change', function () {
        filterSubjects();
    });

    // Form submission
    document.getElementById('subjectForm').addEventListener('submit', function (e) {
        e.preventDefault();
        saveSubject();
    });
}

// Load subjects from API
async function loadSubjects() {
    try {
        // GET không cần gửi Authorization
        const response = await fetch(SUBJECTS_API, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            subjects = data;
            displaySubjects();
            updateTeacherFilter();
        } else {
            console.error('Failed to load subjects:', response.status);
            showNotification('Lỗi khi tải danh sách môn học', 'error');
        }
    } catch (error) {
        console.error('Error loading subjects:', error);
        showNotification('Lỗi kết nối khi tải môn học', 'error');
    }
}

// Load teachers for dropdown
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
            updateTeacherDropdown();
        } else {
            console.error('Failed to load teachers:', response.status);
        }
    } catch (error) {
        console.error('Error loading teachers:', error);
    }
}

// Display subjects in table
function displaySubjects() {
    const tbody = document.getElementById('subjectsTable');
    tbody.innerHTML = '';

    subjects.forEach(subject => {
        const teacher = teachers.find(t => t.id === subject.teacher) || {};
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${subject.subject_code || ''}</td>
            <td>${subject.name || ''}</td>
            <td>${teacher.name || 'N/A'}</td>
            <td>${subject.time || ''}</td>
            <td>${subject.room || ''}</td>
            <td>${subject.credits || ''}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editSubject(${subject.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteSubject(${subject.id}, '${subject.name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Update teacher dropdown in form
function updateTeacherDropdown() {
    const select = document.getElementById('subjectTeacher');
    select.innerHTML = '<option value="">Chọn giảng viên</option>';

    teachers.forEach(teacher => {
        const option = document.createElement('option');
        option.value = teacher.id;
        option.textContent = `${teacher.name} (${teacher.teacher_code})`;
        select.appendChild(option);
    });
}

// Update teacher filter dropdown
function updateTeacherFilter() {
    const select = document.getElementById('filterTeacher');
    const currentValue = select.value;

    select.innerHTML = '<option value="">Tất cả giảng viên</option>';

    const uniqueTeachers = [...new Set(subjects.map(s => s.teacher))];
    uniqueTeachers.forEach(teacherId => {
        const teacher = teachers.find(t => t.id === teacherId);
        if (teacher) {
            const option = document.createElement('option');
            option.value = teacherId;
            option.textContent = teacher.name;
            if (teacherId == currentValue) {
                option.selected = true;
            }
            select.appendChild(option);
        }
    });
}

// Filter subjects
function filterSubjects() {
    const searchTerm = document.getElementById('searchSubject').value.toLowerCase();
    const teacherFilter = document.getElementById('filterTeacher').value;

    const filtered = subjects.filter(subject => {
        const matchesSearch = !searchTerm ||
            (subject.subject_code && subject.subject_code.toLowerCase().includes(searchTerm)) ||
            (subject.name && subject.name.toLowerCase().includes(searchTerm));

        const matchesTeacher = !teacherFilter || subject.teacher == teacherFilter;

        return matchesSearch && matchesTeacher;
    });

    displayFilteredSubjects(filtered);
}

// Display filtered subjects
function displayFilteredSubjects(filteredSubjects) {
    const tbody = document.getElementById('subjectsTable');
    tbody.innerHTML = '';

    filteredSubjects.forEach(subject => {
        const teacher = teachers.find(t => t.id === subject.teacher) || {};
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${subject.subject_code || ''}</td>
            <td>${subject.name || ''}</td>
            <td>${teacher.name || 'N/A'}</td>
            <td>${subject.time || ''}</td>
            <td>${subject.room || ''}</td>
            <td>${subject.credits || ''}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editSubject(${subject.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteSubject(${subject.id}, '${subject.name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Open modal for adding new subject
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
    if (modalId === 'addSubjectModal') {
        resetForm();
    }
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Reset form
function resetForm() {
    document.getElementById('subjectForm').reset();
    document.getElementById('subjectId').value = '';
    document.getElementById('subjectModalTitle').textContent = 'Thêm môn học mới';
    document.getElementById('subjectSubmitBtn').textContent = 'Thêm môn học';
    currentSubjectId = null;
}

// Edit subject
function editSubject(id) {
    const subject = subjects.find(s => s.id === id);
    if (subject) {
        currentSubjectId = id;
        document.getElementById('subjectId').value = subject.id;
        document.getElementById('subjectCode').value = subject.subject_code || '';
        document.getElementById('subjectName').value = subject.name || '';
        document.getElementById('subjectTeacher').value = subject.teacher || '';
        document.getElementById('subjectTime').value = subject.time || '';
        document.getElementById('subjectRoom').value = subject.room || '';
        document.getElementById('subjectCredits').value = subject.credits || '';
        document.getElementById('subjectDescription').value = subject.description || '';

        document.getElementById('subjectModalTitle').textContent = 'Chỉnh sửa môn học';
        document.getElementById('subjectSubmitBtn').textContent = 'Cập nhật môn học';

        openModal('addSubjectModal');
    }
}

// Save subject (create or update)
async function saveSubject() {
    const formData = new FormData(document.getElementById('subjectForm'));
    const subjectData = {
        subject_code: formData.get('subject_code'),
        name: formData.get('name'),
        teacher: formData.get('teacher'),
        time: formData.get('time'),
        room: formData.get('room'),
        credits: formData.get('credits') ? parseInt(formData.get('credits')) : null,
        description: formData.get('description')
    };

    try {
        const token = localStorage.getItem('accessToken');
        const url = currentSubjectId ? `${SUBJECTS_API}${currentSubjectId}/` : `${SUBJECTS_API}create/`;
        const method = currentSubjectId ? 'PUT' : 'POST';

        // Log dữ liệu gửi lên
        console.log('Subject data gửi lên:', subjectData);
        console.log('URL:', url, 'Method:', method);

        const response = await fetch(url, {
            method: method,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(subjectData)
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(
                currentSubjectId ? 'Cập nhật môn học thành công!' : 'Thêm môn học thành công!',
                'success'
            );
            closeModal('addSubjectModal');
            loadSubjects();
        } else {
            let errorText = '';
            try {
                const error = await response.json();
                console.error('Failed to save subject:', error);

                if (error.subject_code) {
                    errorText = 'Mã môn học đã tồn tại!';
                } else if (error.name) {
                    errorText = 'Tên môn học đã tồn tại!';
                } else if (error.error) {
                    errorText = error.error;
                } else {
                    errorText = JSON.stringify(error);
                }
            } catch (e) {
                errorText = 'Lỗi không xác định hoặc không đọc được phản hồi từ server.';
                console.error('Error parsing error response:', e);
            }
            showNotification(errorText, 'error');
        }
    } catch (error) {
        console.error('Error saving subject:', error);
        showNotification('Lỗi kết nối khi lưu môn học', 'error');
    }
}

// Delete subject
function deleteSubject(id, name) {
    deleteSubjectId = id;
    document.getElementById('deleteSubjectName').textContent = name;
    openModal('deleteModal');
}

// Confirm delete
async function confirmDelete() {
    if (!deleteSubjectId) return;

    try {
        const token = localStorage.getItem('accessToken');
        const response = await fetch(`${SUBJECTS_API}${deleteSubjectId}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            showNotification('Xóa môn học thành công!', 'success');
            closeModal('deleteModal');
            loadSubjects();
        } else {
            console.error('Failed to delete subject:', response.status);
            showNotification('Lỗi khi xóa môn học', 'error');
        }
    } catch (error) {
        console.error('Error deleting subject:', error);
        showNotification('Lỗi kết nối khi xóa môn học', 'error');
    }
}

// Export subjects to Excel
function exportSubjects() {
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