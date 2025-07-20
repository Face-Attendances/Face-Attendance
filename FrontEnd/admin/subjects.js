// Global variables
let subjects = [];
let currentSubjectId = null;
let deleteSubjectId = null;

// API endpoints
const SUBJECTS_API_BASE_URL = 'http://localhost:8000/api';
const SUBJECTS_API = `${SUBJECTS_API_BASE_URL}/database/subjects/`;

// Authentication helper
async function getAuthHeaders() {
    const token = localStorage.getItem('accessToken');

    if (!token) {
        showNotification('Không tìm thấy token. Vui lòng đăng nhập lại.', 'error');
        setTimeout(() => {
            window.location.href = '../login/login.html';
        }, 2000);
        return null;
    }

    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    };
}

async function makeAuthenticatedRequest(url, options = {}) {
    const headers = await getAuthHeaders();
    if (!headers) return null;

    const response = await fetch(url, {
        ...options,
        headers: {
            ...headers,
            ...options.headers
        }
    });

    // If unauthorized, try to refresh token
    if (response.status === 401) {
        showNotification('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.', 'warning');
        setTimeout(() => {
            localStorage.removeItem('accessToken');
            localStorage.removeItem('refreshToken');
            window.location.href = '../login/login.html';
        }, 2000);
        return null;
    }

    return response;
}

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadSubjects();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    const searchSubject = document.getElementById('searchSubject');
    if (searchSubject) {
        searchSubject.addEventListener('input', function () {
            filterSubjects();
        });
    }



    // Form submission
    const subjectForm = document.getElementById('subjectForm');
    if (subjectForm) {
        subjectForm.addEventListener('submit', function (e) {
            e.preventDefault();
            saveSubject();
        });
    }
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
        } else {
            console.error('Failed to load subjects:', response.status);
            showNotification('Lỗi khi tải danh sách môn học', 'error');
        }
    } catch (error) {
        console.error('Error loading subjects:', error);
        showNotification('Lỗi kết nối khi tải môn học', 'error');
    }
}



// Display subjects in table
function displaySubjects() {
    const tbody = document.getElementById('subjectsTable');
    if (!tbody) return;

    subjects.forEach(subject => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${subject.subject_code || ''}</td>
            <td>${subject.subject_name || ''}</td>
            <td>${subject.credits || ''}</td>
            <td>${subject.description || ''}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editSubject(${subject.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteSubject(${subject.id}, '${subject.subject_name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}



// Filter subjects
function filterSubjects() {
    const searchSubject = /** @type {HTMLInputElement} */ (document.getElementById('searchSubject'));
    if (!searchSubject) return;

    const searchTerm = searchSubject.value.toLowerCase();

    const filtered = subjects.filter(subject => {
        const matchesSearch = !searchTerm ||
            (subject.subject_code && subject.subject_code.toLowerCase().includes(searchTerm)) ||
            (subject.subject_name && subject.subject_name.toLowerCase().includes(searchTerm));

        return matchesSearch;
    });

    displayFilteredSubjects(filtered);
}

// Display filtered subjects
function displayFilteredSubjects(filteredSubjects) {
    const tbody = document.getElementById('subjectsTable');
    if (!tbody) return;

    filteredSubjects.forEach(subject => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${subject.subject_code || ''}</td>
            <td>${subject.subject_name || ''}</td>
            <td>${subject.credits || ''}</td>
            <td>${subject.description || ''}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editSubject(${subject.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteSubject(${subject.id}, '${subject.subject_name}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Open modal for adding new subject
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        if (modalId === 'addSubjectModal') {
            resetForm();
        }
    }
}

// Close modal
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Reset form
function resetForm() {
    const form = /** @type {HTMLFormElement} */ (document.getElementById('subjectForm'));
    const subjectId = /** @type {HTMLInputElement} */ (document.getElementById('subjectId'));
    const subjectModalTitle = document.getElementById('subjectModalTitle');
    const subjectSubmitBtn = document.getElementById('subjectSubmitBtn');

    if (form) {
        form.reset();
    }
    if (subjectId) {
        subjectId.value = '';
    }
    if (subjectModalTitle) {
        subjectModalTitle.textContent = 'Thêm môn học mới';
    }
    if (subjectSubmitBtn) {
        subjectSubmitBtn.textContent = 'Thêm môn học';
    }
    currentSubjectId = null;
}

// Edit subject
function editSubject(id) {
    const subject = subjects.find(s => s.id === id);
    if (subject) {
        currentSubjectId = id;
        const subjectId = /** @type {HTMLInputElement} */ (document.getElementById('subjectId'));
        const subjectCode = /** @type {HTMLInputElement} */ (document.getElementById('subjectCode'));
        const subjectName = /** @type {HTMLInputElement} */ (document.getElementById('subjectName'));
        const subjectCredits = /** @type {HTMLInputElement} */ (document.getElementById('subjectCredits'));
        const subjectDescription = /** @type {HTMLTextAreaElement} */ (document.getElementById('subjectDescription'));
        const subjectModalTitle = document.getElementById('subjectModalTitle');
        const subjectSubmitBtn = document.getElementById('subjectSubmitBtn');

        if (subjectId) {
            subjectId.value = subject.id;
        }
        if (subjectCode) {
            subjectCode.value = subject.subject_code || '';
        }
        if (subjectName) {
            subjectName.value = subject.subject_name || '';
        }
        if (subjectCredits) {
            subjectCredits.value = subject.credits || '';
        }
        if (subjectDescription) {
            subjectDescription.value = subject.description || '';
        }
        if (subjectModalTitle) {
            subjectModalTitle.textContent = 'Chỉnh sửa môn học';
        }
        if (subjectSubmitBtn) {
            subjectSubmitBtn.textContent = 'Cập nhật môn học';
        }

        openModal('addSubjectModal');
    }
}

// Save subject (create or update)
async function saveSubject() {
    const form = /** @type {HTMLFormElement} */ (document.getElementById('subjectForm'));
    if (!form) return;

    const formData = new FormData(form);
    const creditsValue = formData.get('credits');
    const subjectData = {
        subject_code: formData.get('subject_code'),
        subject_name: formData.get('subject_name'),
        credits: creditsValue ? parseInt(String(creditsValue)) : null,
        description: formData.get('description')
    };

    try {
        const url = currentSubjectId ? `${SUBJECTS_API}${currentSubjectId}/update/` : `${SUBJECTS_API}create/`;
        const method = currentSubjectId ? 'PUT' : 'POST';

        // Log dữ liệu gửi lên
        console.log('Subject data gửi lên:', subjectData);
        console.log('URL:', url, 'Method:', method);

        const response = await makeAuthenticatedRequest(url, {
            method: method,
            body: JSON.stringify(subjectData)
        });

        if (!response) {
            showNotification('Lỗi xác thực. Vui lòng đăng nhập lại.', 'error');
            return;
        }

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
    const deleteSubjectName = document.getElementById('deleteSubjectName');
    if (deleteSubjectName) {
        deleteSubjectName.textContent = name;
    }
    openModal('deleteModal');
}

// Confirm delete
async function confirmDelete() {
    if (!deleteSubjectId) {
        showNotification('Không có môn học nào được chọn để xóa', 'error');
        return;
    }

    try {
        console.log('🗑️ Deleting subject ID:', deleteSubjectId);

        const response = await makeAuthenticatedRequest(`${SUBJECTS_API}${deleteSubjectId}/delete/`, {
            method: 'DELETE'
        });

        if (!response) {
            showNotification('Lỗi xác thực. Vui lòng đăng nhập lại.', 'error');
            return;
        }

        console.log('Delete response status:', response.status);
        console.log('Delete response ok:', response.ok);

        if (response.ok) {
            // Handle both 200 and 204 status codes as success
            if (response.status === 204 || response.status === 200) {
                showNotification('Xóa môn học thành công!', 'success');
                closeModal('deleteModal');
                deleteSubjectId = null; // Reset
                await loadSubjects(); // Reload data
            } else {
                const errorData = await response.json();
                showNotification('Lỗi khi xóa: ' + (errorData.message || 'Unknown error'), 'error');
            }
        } else {
            let errorMessage = 'Lỗi khi xóa môn học';
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorData.error || errorMessage;
            } catch (e) {
                console.log('Could not parse error response');
            }
            console.error('Failed to delete subject:', response.status, errorMessage);
            showNotification(errorMessage, 'error');
        }
    } catch (error) {
        console.error('Network error deleting subject:', error);
        showNotification('Lỗi kết nối khi xóa môn học: ' + error.message, 'error');
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
            /** @type {HTMLElement} */ (modal).style.display = 'none';
        }
    });
} 