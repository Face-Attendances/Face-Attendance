$(document).ready(function () {
    let currentPage = 1;
    let totalPages = 1;
    let attendanceData = [];

    // Get authentication token
    const token = localStorage.getItem('accessToken');

    // Setup default AJAX settings for authentication
    $.ajaxSetup({
        beforeSend: function (xhr) {
            if (token) {
                xhr.setRequestHeader('Authorization', 'Bearer ' + token);
            }
        }
    });

    // Load initial data
    loadAttendanceLog();
    loadFilters();

    // Event listeners
    $('#filterBtn').click(function () {
        currentPage = 1;
        loadAttendanceLog();
    });

    $('#exportBtn').click(function () {
        exportAttendanceData();
    });

    $('#prevPage').click(function () {
        if (currentPage > 1) {
            currentPage--;
            loadAttendanceLog();
        }
    });

    $('#nextPage').click(function () {
        if (currentPage < totalPages) {
            currentPage++;
            loadAttendanceLog();
        }
    });

    function loadAttendanceLog() {
        const dateFilter = $('#dateFilter').val();
        const subjectFilter = $('#subjectFilter').val();
        const studentFilter = $('#studentFilter').val();

        // Show loading message
        showErrorMessage('', false);
        $('#attendanceTableBody').html('<tr><td colspan="8" style="text-align: center; padding: 20px;"><i class="fas fa-spinner fa-spin"></i> Đang tải dữ liệu...</td></tr>');

        console.log('Loading attendance data...', {
            dateFilter, subjectFilter, studentFilter, token: token ? 'exists' : 'missing'
        });

        $.ajax({
            url: 'http://localhost:8000/api/database/attendance/',
            method: 'GET',
            data: {
                page: currentPage,
                date: dateFilter,
                subject: subjectFilter,
                student: studentFilter
            },
            success: function (response) {
                console.log('API Response:', response);

                // Backend returns array directly, not wrapped in success object
                if (Array.isArray(response)) {
                    attendanceData = response;
                    totalPages = Math.ceil(response.length / 20) || 1; // Assume 20 per page
                    displayAttendanceData();
                    updatePagination();
                } else if (response.success) {
                    attendanceData = response.data.results || response.data;
                    totalPages = response.data.total_pages || 1;
                    displayAttendanceData();
                    updatePagination();
                } else {
                    showErrorMessage('Lỗi tải dữ liệu: ' + (response.message || 'Lỗi không xác định'), true);
                    showAlert('Error loading attendance data: ' + (response.message || 'Unknown error'), 'error');
                }
            },
            error: function (xhr, status, error) {
                console.error('API Error Details:', {
                    status: xhr.status,
                    statusText: xhr.statusText,
                    responseText: xhr.responseText,
                    error: error
                });

                let errorMsg = 'Lỗi kết nối API: ';
                if (xhr.status === 401) {
                    errorMsg += 'Không có quyền truy cập (401)';
                } else if (xhr.status === 404) {
                    errorMsg += 'Không tìm thấy endpoint (404)';
                } else if (xhr.status === 500) {
                    errorMsg += 'Lỗi server (500)';
                } else {
                    errorMsg += `${xhr.status} - ${error}`;
                }

                showErrorMessage(errorMsg, true);
                showAlert('Error loading attendance data: ' + error, 'error');

                // Show empty table
                $('#attendanceTableBody').html('<tr><td colspan="8" style="text-align: center; padding: 20px; color: #dc3545;">Không thể tải dữ liệu</td></tr>');
            }
        });
    }

    function loadFilters() {
        // Load subjects
        $.ajax({
            url: 'http://localhost:8000/api/database/subjects/',
            method: 'GET',
            success: function (response) {
                const subjectSelect = $('#subjectFilter');
                subjectSelect.empty().append('<option value="">All Subjects</option>');

                // Backend returns array directly
                const subjects = Array.isArray(response) ? response : (response.data || []);
                subjects.forEach(function (subject) {
                    subjectSelect.append(`<option value="${subject.id}">${subject.subject_name}</option>`);
                });
            }
        });

        // Load students
        $.ajax({
            url: 'http://localhost:8000/api/database/students/',
            method: 'GET',
            success: function (response) {
                const studentSelect = $('#studentFilter');
                studentSelect.empty().append('<option value="">All Students</option>');

                // Backend returns array directly
                const students = Array.isArray(response) ? response : (response.data || []);
                students.forEach(function (student) {
                    studentSelect.append(`<option value="${student.id}">${student.name}</option>`);
                });
            }
        });
    }

    function displayAttendanceData() {
        const tbody = $('#attendanceTableBody');
        tbody.empty();

        if (attendanceData.length === 0) {
            tbody.append('<tr><td colspan="8" class="text-center">No attendance records found</td></tr>');
            return;
        }

        attendanceData.forEach(function (record) {
            // Format timestamp
            const timestamp = new Date(record.timestamp);
            const dateStr = timestamp.toLocaleDateString('vi-VN');
            const timeStr = timestamp.toLocaleTimeString('vi-VN');

            const row = `
                <tr>
                    <td>${dateStr}</td>
                    <td>${timeStr}</td>
                    <td>${record.student_name || 'N/A'}</td>
                    <td>${record.subject_name || 'N/A'}</td>
                    <td>${record.teacher_name || 'N/A'}</td>
                    <td>
                        <span class="status-badge status-${record.status}">
                            ${record.status.charAt(0).toUpperCase() + record.status.slice(1)}
                        </span>
                    </td>
                    <td>${record.face_detection_confidence ? record.face_detection_confidence.toFixed(1) + '%' : 'N/A'}</td>
                    <td>
                        <button class="btn btn-sm btn-info view-details" data-id="${record.id}">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-danger delete-record" data-id="${record.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
            tbody.append(row);
        });

        // Bind event handlers for buttons
        $('.view-details').off('click').on('click', function () {
            const id = $(this).data('id');
            viewRecordDetails(id);
        });

        $('.delete-record').off('click').on('click', function () {
            const id = $(this).data('id');
            deleteRecord(id);
        });
    }

    function updatePagination() {
        $('#pageInfo').text(`Page ${currentPage} of ${totalPages}`);
        $('#prevPage').prop('disabled', currentPage <= 1);
        $('#nextPage').prop('disabled', currentPage >= totalPages);
    }

    function viewRecordDetails(recordId) {
        const record = attendanceData.find(r => r.id === recordId);
        if (record) {
            const timestamp = new Date(record.timestamp);
            const dateStr = timestamp.toLocaleDateString('vi-VN');
            const timeStr = timestamp.toLocaleTimeString('vi-VN');

            const details = `
                <div class="record-details">
                    <h3>Chi tiết điểm danh</h3>
                    <p><strong>Sinh viên:</strong> ${record.student_name || 'N/A'}</p>
                    <p><strong>Môn học:</strong> ${record.subject_name || 'N/A'}</p>
                    <p><strong>Giảng viên:</strong> ${record.teacher_name || 'N/A'}</p>
                    <p><strong>Ngày:</strong> ${dateStr}</p>
                    <p><strong>Thời gian:</strong> ${timeStr}</p>
                    <p><strong>Trạng thái:</strong> ${record.status}</p>
                    <p><strong>Độ chính xác:</strong> ${record.face_detection_confidence ? record.face_detection_confidence.toFixed(1) + '%' : 'N/A'}</p>
                    <p><strong>Người phát hiện:</strong> ${record.detected_by_name || 'Hệ thống'}</p>
                    ${record.image_path ? `<p><strong>Ảnh:</strong> <img src="${record.image_path}" style="max-width: 200px; border-radius: 8px;"></p>` : ''}
                    ${record.notes ? `<p><strong>Ghi chú:</strong> ${record.notes}</p>` : ''}
                </div>
            `;

            showModal('Chi tiết điểm danh', details);
        }
    }

    function deleteRecord(recordId) {
        if (confirm('Bạn có chắc chắn muốn xóa bản ghi điểm danh này?')) {
            $.ajax({
                url: `http://localhost:8000/api/database/attendance/${recordId}/delete/`,
                method: 'DELETE',
                success: function (response) {
                    if (response.success) {
                        showAlert('Xóa bản ghi thành công', 'success');
                        loadAttendanceLog();
                    } else {
                        showAlert('Lỗi khi xóa: ' + (response.message || 'Unknown error'), 'error');
                    }
                },
                error: function (xhr, status, error) {
                    showAlert('Lỗi khi xóa: ' + error, 'error');
                    console.error('Delete Error:', xhr.responseText);
                }
            });
        }
    }

    function exportAttendanceData() {
        const dateFilter = $('#dateFilter').val();
        const subjectFilter = $('#subjectFilter').val();
        const studentFilter = $('#studentFilter').val();

        const params = new URLSearchParams({
            date: dateFilter,
            subject: subjectFilter,
            student: studentFilter,
            export: 'true'
        });

        window.open(`http://localhost:8000/api/database/attendance/?${params.toString()}`, '_blank');
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    function showErrorMessage(message, show) {
        const errorDiv = $('#errorMessage');
        if (show && message) {
            errorDiv.text(message).show();
        } else {
            errorDiv.hide();
        }
    }

    function showAlert(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
        const alert = $(`<div class="alert ${alertClass}">${message}</div>`);
        $('.main-container').prepend(alert);
        setTimeout(() => alert.fadeOut(), 3000);
    }

    function showModal(title, content) {
        const modal = $(`
            <div class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>${title}</h3>
                        <span class="close">&times;</span>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                </div>
            </div>
        `);

        $('body').append(modal);

        $('.close').click(function () {
            modal.remove();
        });

        $(window).click(function (e) {
            if (e.target === modal[0]) {
                modal.remove();
            }
        });
    }
}); 