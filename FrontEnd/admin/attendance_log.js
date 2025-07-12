$(document).ready(function () {
    let currentPage = 1;
    let totalPages = 1;
    let attendanceData = [];

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

        $.ajax({
            url: 'http://localhost:8000/api/attendance/log/',
            method: 'GET',
            data: {
                page: currentPage,
                date: dateFilter,
                subject: subjectFilter,
                student: studentFilter
            },
            success: function (response) {
                if (response.success) {
                    attendanceData = response.data.results || response.data;
                    totalPages = response.data.total_pages || 1;
                    displayAttendanceData();
                    updatePagination();
                } else {
                    showAlert('Error loading attendance data: ' + response.message, 'error');
                }
            },
            error: function (xhr, status, error) {
                showAlert('Error loading attendance data: ' + error, 'error');
            }
        });
    }

    function loadFilters() {
        // Load subjects
        $.ajax({
            url: 'http://localhost:8000/api/database/subjects/',
            method: 'GET',
            success: function (response) {
                if (response.success) {
                    const subjectSelect = $('#subjectFilter');
                    response.data.forEach(function (subject) {
                        subjectSelect.append(`<option value="${subject.id}">${subject.name}</option>`);
                    });
                }
            }
        });

        // Load students
        $.ajax({
            url: 'http://localhost:8000/api/database/students/',
            method: 'GET',
            success: function (response) {
                if (response.success) {
                    const studentSelect = $('#studentFilter');
                    response.data.forEach(function (student) {
                        studentSelect.append(`<option value="${student.id}">${student.name} (${student.student_code})</option>`);
                    });
                }
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
            const row = `
                <tr>
                    <td>${formatDate(record.date)}</td>
                    <td>${record.time}</td>
                    <td>${record.student_name} (${record.student_code})</td>
                    <td>${record.subject_name}</td>
                    <td>${record.teacher_name}</td>
                    <td>
                        <span class="status-badge ${record.status.toLowerCase()}">
                            ${record.status}
                        </span>
                    </td>
                    <td>${record.confidence ? (record.confidence * 100).toFixed(1) + '%' : 'N/A'}</td>
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

        // Add event listeners for action buttons
        $('.view-details').click(function () {
            const recordId = $(this).data('id');
            viewRecordDetails(recordId);
        });

        $('.delete-record').click(function () {
            const recordId = $(this).data('id');
            deleteRecord(recordId);
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
            const details = `
                <div class="record-details">
                    <h3>Attendance Record Details</h3>
                    <p><strong>Student:</strong> ${record.student_name} (${record.student_code})</p>
                    <p><strong>Subject:</strong> ${record.subject_name}</p>
                    <p><strong>Teacher:</strong> ${record.teacher_name}</p>
                    <p><strong>Date:</strong> ${formatDate(record.date)}</p>
                    <p><strong>Time:</strong> ${record.time}</p>
                    <p><strong>Status:</strong> ${record.status}</p>
                    <p><strong>Confidence:</strong> ${record.confidence ? (record.confidence * 100).toFixed(1) + '%' : 'N/A'}</p>
                    ${record.image_path ? `<p><strong>Image:</strong> <img src="${record.image_path}" style="max-width: 200px;"></p>` : ''}
                </div>
            `;

            showModal('Attendance Details', details);
        }
    }

    function deleteRecord(recordId) {
        if (confirm('Are you sure you want to delete this attendance record?')) {
            $.ajax({
                url: `http://localhost:8000/api/attendance/log/${recordId}/`,
                method: 'DELETE',
                success: function (response) {
                    if (response.success) {
                        showAlert('Attendance record deleted successfully', 'success');
                        loadAttendanceLog();
                    } else {
                        showAlert('Error deleting record: ' + response.message, 'error');
                    }
                },
                error: function (xhr, status, error) {
                    showAlert('Error deleting record: ' + error, 'error');
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

        window.open(`http://localhost:8000/api/attendance/log/?${params.toString()}`, '_blank');
    }

    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    function showAlert(message, type) {
        const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
        const alert = $(`<div class="alert ${alertClass}">${message}</div>`);
        $('.content').prepend(alert);
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