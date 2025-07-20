// Global variables
let teacherSubjects = [];
let teachers = [];
let subjects = [];
let currentTeacherSubjectId = null;
let deleteTeacherSubjectId = null;

// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const TEACHER_SUBJECTS_API = `${API_BASE_URL}/database/teacher-subjects/`;
const TEACHERS_API = `${API_BASE_URL}/database/teachers/`;
const SUBJECTS_API = `${API_BASE_URL}/database/subjects/`;

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadTeacherSubjects();
    loadTeachers();
    loadSubjects();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    document.getElementById('searchTeacherSubject').addEventListener('input', function () {
        filterTeacherSubjects();
    });

    // Filter functionality
    document.getElementById('teacherFilter').addEventListener('change', function () {
        filterTeacherSubjects();
    });

    document.getElementById('subjectFilter').addEventListener('change', function () {
        filterTeacherSubjects();
    });

    // Form submission
    document.getElementById('teacherSubjectForm').addEventListener('submit', function (e) {
        e.preventDefault();
        saveTeacherSubject();
    });
}

// Load teacher subjects from API
async function loadTeacherSubjects() {
    try {
        const response = await fetch(`${TEACHER_SUBJECTS_API}details/`, {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                teacherSubjects = data.data;
                displayTeacherSubjects();
                updateFilters();
            } else {
                console.error('API Error:', data.error);
                showNotification('Lỗi khi tải danh sách môn giảng dạy', 'error');
            }
        } else {
            console.error('Failed to load teacher subjects:', response.status);
            showNotification('Lỗi khi tải danh sách môn giảng dạy', 'error');
        }
    } catch (error) {
        console.error('Error loading teacher subjects:', error);
        showNotification('Lỗi kết nối khi tải môn giảng dạy', 'error');
    }
}

// Load teachers for dropdown
async function loadTeachers() {
    try {
        const response = await fetch(TEACHERS_API);
        if (response.ok) {
            teachers = await response.json();
            updateTeacherSelect();
        }
    } catch (error) {
        console.error('Error loading teachers:', error);
    }
}

// Load subjects for dropdown
async function loadSubjects() {
    try {
        const response = await fetch(SUBJECTS_API);
        if (response.ok) {
            subjects = await response.json();
            updateSubjectSelect();
        }
    } catch (error) {
        console.error('Error loading subjects:', error);
    }
}

// Display teacher subjects in table
function displayTeacherSubjects(teacherSubjectsToShow = teacherSubjects) {
    const tbody = document.getElementById('teacherSubjectsTable');
    tbody.innerHTML = '';

    if (teacherSubjectsToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">Không có dữ liệu môn giảng dạy</td></tr>';
        return;
    }

    teacherSubjectsToShow.forEach(ts => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${ts.id}</td>
            <td>${ts.teacher_name || 'N/A'}</td>
            <td>${ts.teacher_code || 'N/A'}</td>
            <td>${ts.subject_name || 'N/A'}</td>
            <td>${ts.subject_code || 'N/A'}</td>
            <td>${ts.semester || 'N/A'}</td>
            <td>${ts.academic_year || 'N/A'}</td>
            <td>${ts.student_count || 0}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editTeacherSubject(${ts.id})" title="Sửa">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteTeacherSubject(${ts.id}, '${ts.teacher_name} - ${ts.subject_name}')" title="Xóa">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Filter teacher subjects
function filterTeacherSubjects() {
    const searchTerm = document.getElementById('searchTeacherSubject').value.toLowerCase();
    const teacherFilter = document.getElementById('teacherFilter').value;
    const subjectFilter = document.getElementById('subjectFilter').value;

    const filtered = teacherSubjects.filter(ts => {
        const matchesSearch = !searchTerm ||
            (ts.teacher_name && ts.teacher_name.toLowerCase().includes(searchTerm)) ||
            (ts.subject_name && ts.subject_name.toLowerCase().includes(searchTerm)) ||
            (ts.teacher_code && ts.teacher_code.toLowerCase().includes(searchTerm)) ||
            (ts.subject_code && ts.subject_code.toLowerCase().includes(searchTerm));

        const matchesTeacher = !teacherFilter || ts.teacher_code === teacherFilter;
        const matchesSubject = !subjectFilter || ts.subject_code === subjectFilter;

        return matchesSearch && matchesTeacher && matchesSubject;
    });

    displayTeacherSubjects(filtered);
}

// Update filter dropdowns
function updateFilters() {
    updateTeacherFilter();
    updateSubjectFilter();
}

// Update teacher filter
function updateTeacherFilter() {
    const select = document.getElementById('teacherFilter');
    const currentValue = select.value;

    select.innerHTML = '<option value="">Tất cả giảng viên</option>';

    const uniqueTeachers = [...new Set(teacherSubjects.map(ts => ts.teacher_code).filter(t => t))];
    uniqueTeachers.forEach(teacherCode => {
        const teacher = teacherSubjects.find(ts => ts.teacher_code === teacherCode);
        const option = document.createElement('option');
        option.value = teacherCode;
        option.textContent = teacher ? teacher.teacher_name : teacherCode;
        if (teacherCode === currentValue) {
            option.selected = true;
        }
        select.appendChild(option);
    });
}

// Update subject filter
function updateSubjectFilter() {
    const select = document.getElementById('subjectFilter');
    const currentValue = select.value;

    select.innerHTML = '<option value="">Tất cả môn học</option>';

    const uniqueSubjects = [...new Set(teacherSubjects.map(ts => ts.subject_code).filter(s => s))];
    uniqueSubjects.forEach(subjectCode => {
        const subject = teacherSubjects.find(ts => ts.subject_code === subjectCode);
        const option = document.createElement('option');
        option.value = subjectCode;
        option.textContent = subject ? subject.subject_name : subjectCode;
        if (subjectCode === currentValue) {
            option.selected = true;
        }
        select.appendChild(option);
    });
}

// Update teacher select dropdown
function updateTeacherSelect() {
    const select = document.getElementById('teacherSelect');
    select.innerHTML = '<option value="">-- Chọn giảng viên --</option>';

    teachers.forEach(teacher => {
        const option = document.createElement('option');
        option.value = teacher.id;
        option.textContent = `${teacher.name} (${teacher.teacher_code})`;
        select.appendChild(option);
    });
}

// Update subject select dropdown
function updateSubjectSelect() {
    const select = document.getElementById('subjectSelect');
    select.innerHTML = '<option value="">-- Chọn môn học --</option>';

    subjects.forEach(subject => {
        const option = document.createElement('option');
        option.value = subject.id;
        option.textContent = `${subject.subject_name} (${subject.subject_code})`;
        select.appendChild(option);
    });
}

// Add new teacher subject
function addNewTeacherSubject() {
    currentTeacherSubjectId = null;
    resetForm();
    openModal('teacherSubjectModal');
}

// Open modal
function openModal(modalId) {
    document.getElementById(modalId).style.display = 'block';
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Reset form
function resetForm() {
    document.getElementById('teacherSubjectForm').reset();
    document.getElementById('teacherSubjectId').value = '';
    document.getElementById('teacherSubjectModalTitle').textContent = 'Thêm môn giảng dạy mới';
    document.getElementById('teacherSubjectSubmitBtn').textContent = 'Thêm môn giảng dạy';
    currentTeacherSubjectId = null;
}

// Edit teacher subject
function editTeacherSubject(id) {
    const teacherSubject = teacherSubjects.find(ts => ts.id === id);
    if (!teacherSubject) return;

    currentTeacherSubjectId = id;
    document.getElementById('teacherSubjectId').value = teacherSubject.id;
    document.getElementById('teacherSelect').value = teacherSubject.teacher_id;
    document.getElementById('subjectSelect').value = teacherSubject.subject_id;
    document.getElementById('semester').value = teacherSubject.semester || '';
    document.getElementById('academicYear').value = teacherSubject.academic_year || '';

    document.getElementById('teacherSubjectModalTitle').textContent = 'Chỉnh sửa môn giảng dạy';
    document.getElementById('teacherSubjectSubmitBtn').textContent = 'Cập nhật môn giảng dạy';

    openModal('teacherSubjectModal');
}

// Save teacher subject (create or update)
async function saveTeacherSubject() {
    const formData = new FormData(document.getElementById('teacherSubjectForm'));
    const teacherSubjectData = {
        teacher: formData.get('teacher'),
        subject: formData.get('subject'),
        semester: formData.get('semester'),
        academic_year: formData.get('academic_year')
    };

    try {
        let url, method;
        if (currentTeacherSubjectId) {
            url = `${TEACHER_SUBJECTS_API}${currentTeacherSubjectId}/update/`;
            method = 'PUT';
        } else {
            url = `${TEACHER_SUBJECTS_API}create/`;
            method = 'POST';
        }

        const response = await fetch(url, {
            method: method,
            headers: getAuthHeaders(),
            body: JSON.stringify(teacherSubjectData)
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(
                currentTeacherSubjectId ? 'Cập nhật môn giảng dạy thành công!' : 'Thêm môn giảng dạy thành công!',
                'success'
            );
            closeModal('teacherSubjectModal');
            loadTeacherSubjects();
        } else {
            let errorText = '';
            try {
                const error = await response.json();
                if (error.teacher) {
                    errorText = `Giảng viên: ${error.teacher.join(', ')}`;
                } else if (error.subject) {
                    errorText = `Môn học: ${error.subject.join(', ')}`;
                } else if (error.error) {
                    errorText = error.error;
                } else {
                    errorText = JSON.stringify(error);
                }
            } catch (e) {
                errorText = 'Lỗi không xác định';
            }
            showNotification(errorText, 'error');
        }
    } catch (error) {
        console.error('Error saving teacher subject:', error);
        showNotification('Lỗi kết nối khi lưu môn giảng dạy', 'error');
    }
}

// Delete teacher subject
function deleteTeacherSubject(id, name) {
    deleteTeacherSubjectId = id;
    document.getElementById('deleteTeacherSubjectName').textContent = name;
    openModal('deleteModal');
}

// Confirm delete
async function confirmDelete() {
    if (!deleteTeacherSubjectId) return;

    try {
        const response = await fetch(`${TEACHER_SUBJECTS_API}${deleteTeacherSubjectId}/delete/`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        if (response.ok) {
            showNotification('Xóa môn giảng dạy thành công!', 'success');
            closeModal('deleteModal');
            deleteTeacherSubjectId = null;
            loadTeacherSubjects();
        } else {
            let errorMessage = 'Lỗi khi xóa môn giảng dạy';
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorData.error || errorMessage;
            } catch (e) {
                console.log('Could not parse error response');
            }
            showNotification(errorMessage, 'error');
        }
    } catch (error) {
        console.error('Network error deleting teacher subject:', error);
        showNotification('Lỗi kết nối khi xóa môn giảng dạy', 'error');
    }
}

// Clear filters
function clearFilters() {
    document.getElementById('searchTeacherSubject').value = '';
    document.getElementById('teacherFilter').value = '';
    document.getElementById('subjectFilter').value = '';
    displayTeacherSubjects();
}

// Get authentication headers
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

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;

    document.body.appendChild(notification);

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

// Export functions for global access
window.addNewTeacherSubject = addNewTeacherSubject;
window.editTeacherSubject = editTeacherSubject;
window.deleteTeacherSubject = deleteTeacherSubject;
window.confirmDelete = confirmDelete;
window.clearFilters = clearFilters;
window.openModal = openModal;
window.closeModal = closeModal; 