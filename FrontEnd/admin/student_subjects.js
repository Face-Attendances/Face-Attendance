// Global variables
let studentSubjects = [];
let students = [];
let subjects = [];
let currentStudentSubjectId = null;
let deleteStudentSubjectId = null;

// API endpoints
const API_BASE_URL = 'http://localhost:8000/api';
const STUDENT_SUBJECTS_API = `${API_BASE_URL}/database/student-subjects/`;
const STUDENTS_API = `${API_BASE_URL}/database/students/`;
const SUBJECTS_API = `${API_BASE_URL}/database/subjects/`;

// Initialize page
document.addEventListener('DOMContentLoaded', function () {
    loadStudentSubjects();
    loadStudents();
    loadSubjects();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Search functionality
    document.getElementById('searchStudentSubject').addEventListener('input', function () {
        filterStudentSubjects();
    });

    // Filter functionality
    document.getElementById('studentFilter').addEventListener('change', function () {
        filterStudentSubjects();
    });

    document.getElementById('subjectFilter').addEventListener('change', function () {
        filterStudentSubjects();
    });

    document.getElementById('semesterFilter').addEventListener('change', function () {
        filterStudentSubjects();
    });

    // Form submission
    document.getElementById('studentSubjectForm').addEventListener('submit', function (e) {
        e.preventDefault();
        saveStudentSubject();
    });
}

// Load student subjects from API
async function loadStudentSubjects() {
    try {
        const response = await fetch(`${STUDENT_SUBJECTS_API}`, {
            headers: getAuthHeaders()
        });

        if (response.ok) {
            const result = await response.json();
            console.log('API Response:', result);
            if (result.success) {
                studentSubjects = result.data;
                console.log('Student Subjects loaded:', studentSubjects);
                displayStudentSubjects();
                updateFilters();
            } else {
                console.error('API Error:', result.error);
                showNotification('Lỗi khi tải danh sách đăng ký môn học', 'error');
            }
        } else {
            console.error('Failed to load student subjects:', response.status);
            showNotification('Lỗi khi tải danh sách đăng ký môn học', 'error');
        }
    } catch (error) {
        console.error('Error loading student subjects:', error);
        showNotification('Lỗi kết nối khi tải đăng ký môn học', 'error');
    }
}

// Load students for dropdown
async function loadStudents() {
    try {
        const response = await fetch(STUDENTS_API);
        if (response.ok) {
            students = await response.json();
            updateStudentSelect();
        }
    } catch (error) {
        console.error('Error loading students:', error);
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

// Display student subjects in table
function displayStudentSubjects(studentSubjectsToShow = studentSubjects) {
    const tbody = document.getElementById('studentSubjectsTable');
    tbody.innerHTML = '';

    console.log('Displaying student subjects:', studentSubjectsToShow);
    console.log('Type:', typeof studentSubjectsToShow);
    console.log('Is Array:', Array.isArray(studentSubjectsToShow));

    if (!Array.isArray(studentSubjectsToShow)) {
        console.error('studentSubjectsToShow is not an array:', studentSubjectsToShow);
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">Lỗi: Dữ liệu không hợp lệ</td></tr>';
        return;
    }

    if (studentSubjectsToShow.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" style="text-align: center;">Không có dữ liệu đăng ký môn học</td></tr>';
        return;
    }

    studentSubjectsToShow.forEach(ss => {
        const row = document.createElement('tr');
        const registrationDate = ss.registration_date ? new Date(ss.registration_date).toLocaleDateString('vi-VN') : 'N/A';

        row.innerHTML = `
            <td>${ss.id}</td>
            <td>${ss.student_name || 'N/A'}</td>
            <td>${ss.student_code || 'N/A'}</td>
            <td>${ss.subject_name || 'N/A'}</td>
            <td>${ss.subject_code || 'N/A'}</td>
            <td>${ss.semester || 'N/A'}</td>
            <td>${ss.academic_year || 'N/A'}</td>
            <td>${registrationDate}</td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="editStudentSubject(${ss.id})" title="Sửa">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteStudentSubject(${ss.id}, '${ss.student_name} - ${ss.subject_name}')" title="Xóa">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Filter student subjects
function filterStudentSubjects() {
    const searchTerm = document.getElementById('searchStudentSubject').value.toLowerCase();
    const studentFilter = document.getElementById('studentFilter').value;
    const subjectFilter = document.getElementById('subjectFilter').value;
    const semesterFilter = document.getElementById('semesterFilter').value;

    const filtered = studentSubjects.filter(ss => {
        const matchesSearch = !searchTerm ||
            (ss.student_name && ss.student_name.toLowerCase().includes(searchTerm)) ||
            (ss.subject_name && ss.subject_name.toLowerCase().includes(searchTerm)) ||
            (ss.student_code && ss.student_code.toLowerCase().includes(searchTerm)) ||
            (ss.subject_code && ss.subject_code.toLowerCase().includes(searchTerm));

        const matchesStudent = !studentFilter || ss.student_code === studentFilter;
        const matchesSubject = !subjectFilter || ss.subject_code === subjectFilter;
        const matchesSemester = !semesterFilter || ss.semester === semesterFilter;

        return matchesSearch && matchesStudent && matchesSubject && matchesSemester;
    });

    displayStudentSubjects(filtered);
}

// Update filter dropdowns
function updateFilters() {
    updateStudentFilter();
    updateSubjectFilter();
    updateSemesterFilter();
}

// Update student filter
function updateStudentFilter() {
    const select = document.getElementById('studentFilter');
    const currentValue = select.value;

    select.innerHTML = '<option value="">Tất cả sinh viên</option>';

    const uniqueStudents = [...new Set(studentSubjects.map(ss => ss.student_code).filter(s => s))];
    uniqueStudents.forEach(studentCode => {
        const student = studentSubjects.find(ss => ss.student_code === studentCode);
        const option = document.createElement('option');
        option.value = studentCode;
        option.textContent = student ? student.student_name : studentCode;
        if (studentCode === currentValue) {
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

    const uniqueSubjects = [...new Set(studentSubjects.map(ss => ss.subject_code).filter(s => s))];
    uniqueSubjects.forEach(subjectCode => {
        const subject = studentSubjects.find(ss => ss.subject_code === subjectCode);
        const option = document.createElement('option');
        option.value = subjectCode;
        option.textContent = subject ? subject.subject_name : subjectCode;
        if (subjectCode === currentValue) {
            option.selected = true;
        }
        select.appendChild(option);
    });
}

// Update semester filter
function updateSemesterFilter() {
    const select = document.getElementById('semesterFilter');
    const currentValue = select.value;

    select.innerHTML = '<option value="">Tất cả học kỳ</option>';

    const uniqueSemesters = [...new Set(studentSubjects.map(ss => ss.semester).filter(s => s))];
    uniqueSemesters.forEach(semester => {
        const option = document.createElement('option');
        option.value = semester;
        option.textContent = semester;
        if (semester === currentValue) {
            option.selected = true;
        }
        select.appendChild(option);
    });
}

// Update student select dropdown
function updateStudentSelect() {
    const select = document.getElementById('studentSelect');
    select.innerHTML = '<option value="">-- Chọn sinh viên --</option>';

    students.forEach(student => {
        const option = document.createElement('option');
        option.value = student.id;
        option.textContent = `${student.name} (${student.student_code})`;
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

// Add new student subject
function addNewStudentSubject() {
    currentStudentSubjectId = null;
    resetForm();
    openModal('studentSubjectModal');
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
    document.getElementById('studentSubjectForm').reset();
    document.getElementById('studentSubjectId').value = '';
    document.getElementById('studentSubjectModalTitle').textContent = 'Thêm đăng ký môn học mới';
    document.getElementById('studentSubjectSubmitBtn').textContent = 'Thêm đăng ký';

    // Auto-fill current semester and academic year for new registrations
    if (!currentStudentSubjectId) {
        document.getElementById('semester').value = getCurrentSemester();
        document.getElementById('academicYear').value = getCurrentAcademicYear();
    }

    currentStudentSubjectId = null;
}

// Edit student subject
function editStudentSubject(id) {
    const studentSubject = studentSubjects.find(ss => ss.id === id);
    if (!studentSubject) return;

    currentStudentSubjectId = id;
    document.getElementById('studentSubjectId').value = studentSubject.id;
    document.getElementById('studentSelect').value = studentSubject.student_id;
    document.getElementById('subjectSelect').value = studentSubject.subject_id;
    document.getElementById('semester').value = studentSubject.semester || '';
    document.getElementById('academicYear').value = studentSubject.academic_year || '';

    document.getElementById('studentSubjectModalTitle').textContent = 'Chỉnh sửa đăng ký môn học';
    document.getElementById('studentSubjectSubmitBtn').textContent = 'Cập nhật đăng ký';

    openModal('studentSubjectModal');
}

// Save student subject (create or update)
async function saveStudentSubject() {
    const formData = new FormData(document.getElementById('studentSubjectForm'));
    const studentSubjectData = {
        student: formData.get('student'),
        subject: formData.get('subject'),
        semester: formData.get('semester') || getCurrentSemester(),
        academic_year: formData.get('academic_year') || getCurrentAcademicYear()
    };

    // Validation
    if (!studentSubjectData.student) {
        showNotification('Vui lòng chọn sinh viên', 'error');
        return;
    }
    if (!studentSubjectData.subject) {
        showNotification('Vui lòng chọn môn học', 'error');
        return;
    }

    // Check for duplicate registration (only for new registrations)
    if (!currentStudentSubjectId) {
        const isDuplicate = studentSubjects.some(ss =>
            ss.student_id == studentSubjectData.student &&
            ss.subject_id == studentSubjectData.subject &&
            ss.semester === studentSubjectData.semester &&
            ss.academic_year === studentSubjectData.academic_year
        );

        if (isDuplicate) {
            showNotification('Sinh viên đã đăng ký môn học này trong học kỳ và năm học này', 'warning');
            return;
        }
    }

    try {
        let url, method;
        if (currentStudentSubjectId) {
            url = `${STUDENT_SUBJECTS_API}${currentStudentSubjectId}/update/`;
            method = 'PUT';
        } else {
            url = `${STUDENT_SUBJECTS_API}create/`;
            method = 'POST';
        }

        console.log('🔄 Saving student subject:', studentSubjectData);
        console.log('URL:', url, 'Method:', method);

        const response = await fetch(url, {
            method: method,
            headers: getAuthHeaders(),
            body: JSON.stringify(studentSubjectData)
        });

        if (response.ok) {
            const result = await response.json();
            showNotification(
                currentStudentSubjectId ? 'Cập nhật đăng ký môn học thành công!' : 'Thêm đăng ký môn học thành công!',
                'success'
            );
            closeModal('studentSubjectModal');
            loadStudentSubjects();
        } else {
            let errorText = '';
            try {
                const error = await response.json();
                console.error('❌ API Error:', error);

                if (error.student) {
                    errorText = `Sinh viên: ${Array.isArray(error.student) ? error.student.join(', ') : error.student}`;
                } else if (error.subject) {
                    errorText = `Môn học: ${Array.isArray(error.subject) ? error.subject.join(', ') : error.subject}`;
                } else if (error.error) {
                    errorText = error.error;
                } else if (error.detail) {
                    errorText = error.detail;
                } else if (error.message) {
                    errorText = error.message;
                } else {
                    errorText = 'Lỗi không xác định từ server';
                }
            } catch (e) {
                errorText = 'Lỗi không xác định';
                console.error('❌ Error parsing response:', e);
            }
            showNotification(errorText, 'error');
        }
    } catch (error) {
        console.error('❌ Error saving student subject:', error);
        showNotification('Lỗi kết nối khi lưu đăng ký môn học', 'error');
    }
}

// Get current semester
function getCurrentSemester() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;

    if (month >= 8 && month <= 12) {
        return `${year}-1`;
    } else {
        return `${year - 1}-2`;
    }
}

// Get current academic year
function getCurrentAcademicYear() {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;

    if (month >= 8 && month <= 12) {
        return `${year}-${year + 1}`;
    } else {
        return `${year - 1}-${year}`;
    }
}

// Delete student subject
function deleteStudentSubject(id, name) {
    deleteStudentSubjectId = id;
    document.getElementById('deleteStudentSubjectName').textContent = name;
    openModal('deleteModal');
}

// Confirm delete
async function confirmDelete() {
    if (!deleteStudentSubjectId) return;

    try {
        const response = await fetch(`${STUDENT_SUBJECTS_API}${deleteStudentSubjectId}/delete/`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        if (response.ok) {
            showNotification('Xóa đăng ký môn học thành công!', 'success');
            closeModal('deleteModal');
            deleteStudentSubjectId = null;
            loadStudentSubjects();
        } else {
            let errorMessage = 'Lỗi khi xóa đăng ký môn học';
            try {
                const errorData = await response.json();
                errorMessage = errorData.message || errorData.error || errorMessage;
            } catch (e) {
                console.log('Could not parse error response');
            }
            showNotification(errorMessage, 'error');
        }
    } catch (error) {
        console.error('Network error deleting student subject:', error);
        showNotification('Lỗi kết nối khi xóa đăng ký môn học', 'error');
    }
}

// Clear filters
function clearFilters() {
    document.getElementById('searchStudentSubject').value = '';
    document.getElementById('studentFilter').value = '';
    document.getElementById('subjectFilter').value = '';
    document.getElementById('semesterFilter').value = '';
    displayStudentSubjects();
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

// Bulk register students for a subject
async function bulkRegisterStudents() {
    const subjectId = prompt('Nhập ID môn học để đăng ký hàng loạt:');
    if (!subjectId) return;

    const studentIds = prompt('Nhập danh sách ID sinh viên (phân cách bằng dấu phẩy):');
    if (!studentIds) return;

    const studentIdList = studentIds.split(',').map(id => id.trim()).filter(id => id);
    const semester = getCurrentSemester();
    const academicYear = getCurrentAcademicYear();

    let successCount = 0;
    let errorCount = 0;

    for (const studentId of studentIdList) {
        try {
            const registrationData = {
                student: studentId,
                subject: subjectId,
                semester: semester,
                academic_year: academicYear
            };

            const response = await fetch(`${STUDENT_SUBJECTS_API}create/`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(registrationData)
            });

            if (response.ok) {
                successCount++;
            } else {
                errorCount++;
            }
        } catch (error) {
            errorCount++;
        }
    }

    showNotification(`Đăng ký hàng loạt hoàn tất: ${successCount} thành công, ${errorCount} lỗi`,
        errorCount === 0 ? 'success' : 'warning');

    loadStudentSubjects();
}

// Export student subjects data
function exportStudentSubjects() {
    const dataToExport = studentSubjects.map(ss => ({
        'ID': ss.id,
        'Mã sinh viên': ss.student_code || 'N/A',
        'Tên sinh viên': ss.student_name || 'N/A',
        'Mã môn học': ss.subject_code || 'N/A',
        'Tên môn học': ss.subject_name || 'N/A',
        'Học kỳ': ss.semester || 'N/A',
        'Năm học': ss.academic_year || 'N/A',
        'Ngày đăng ký': ss.registration_date ? new Date(ss.registration_date).toLocaleDateString('vi-VN') : 'N/A'
    }));

    // Convert to CSV
    const headers = Object.keys(dataToExport[0]);
    const csvContent = [
        headers.join(','),
        ...dataToExport.map(row => headers.map(header => `"${row[header]}"`).join(','))
    ].join('\n');

    // Download file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `danh_sach_dang_ky_mon_hoc_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showNotification('Đã xuất dữ liệu thành công!', 'success');
}

// Export functions for global access
window.addNewStudentSubject = addNewStudentSubject;
window.editStudentSubject = editStudentSubject;
window.deleteStudentSubject = deleteStudentSubject;
window.confirmDelete = confirmDelete;
window.clearFilters = clearFilters;
window.bulkRegisterStudents = bulkRegisterStudents;
window.exportStudentSubjects = exportStudentSubjects;
window.openModal = openModal;
window.closeModal = closeModal; 