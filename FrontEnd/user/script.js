$(document).ready(function () {
  // 1. Cập nhật thời gian real-time
  function updateDateTime() {
    const now = new Date();
    const dateStr = now.toLocaleDateString('vi-VN');
    const timeStr = now.toLocaleTimeString('vi-VN');

    $('#date').text(`Ngày: ${dateStr}`);
    $('#time').text(`Giờ: ${timeStr}`);
  }

  setInterval(updateDateTime, 1000);
  updateDateTime();

  // 2. Khởi tạo biến
  let isExpanded = false;
  let stream = null;
  let isCameraActive = false;
  let isAttendanceActive = false;
  let selectedSubject = null;
  let userData = null;

  // 3. Load user data
  function loadUserData() {
    const currentUser = localStorage.getItem("currentUser");
    if (currentUser) {
      try {
        userData = JSON.parse(localStorage.getItem("user_" + currentUser));
        if (userData) {
          updateProfileInfo();
          loadAttendanceHistory();
          loadQuickStats();
        } else {
          // Try to load from student data
          loadStudentData(currentUser);
        }
      } catch (error) {
        console.error('Error parsing user data:', error);
        loadStudentData(currentUser);
      }
    } else {
      showToast('Vui lòng đăng nhập lại', 'warning');
      setTimeout(() => {
        window.location.href = '../login/login.html';
      }, 2000);
    }
  }

  // Load student data from API
  function loadStudentData(studentCode) {
    $.ajax({
      url: `http://localhost:8000/api/database/students/`,
      method: 'GET',
      success: function (response) {
        const student = response.find(s => s.student_code === studentCode);
        if (student) {
          userData = {
            fullName: student.name,
            studentID: student.student_code,
            class: student.student_class,
            course: student.course || 'Chưa cập nhật',
            email: student.email,
            phone: student.phone,
            address: student.address
          };
          localStorage.setItem("user_" + studentCode, JSON.stringify(userData));
          updateProfileInfo();
          loadAttendanceHistory();
          loadQuickStats();
        } else {
          showToast('Không tìm thấy thông tin sinh viên', 'error');
        }
      },
      error: function (xhr, status, error) {
        console.error('Lỗi khi tải thông tin sinh viên:', xhr.status);
        showToast('Không thể tải thông tin sinh viên', 'error');
      }
    });
  }

  // 4. Update profile information
  function updateProfileInfo() {
    if (userData) {
      $('#student-name').text(userData.fullName || 'Chưa cập nhật');
      $('#student-id').text(userData.studentID || 'Chưa cập nhật');
      $('#student-class').text(userData.class || 'Chưa cập nhật');
      $('#student-course').text(userData.course || 'Chưa cập nhật');
      $('#student-email').text(userData.email || 'Chưa cập nhật');
      $('#student-phone').text(userData.phone || 'Chưa cập nhật');
      $('#student-address').text(userData.address || 'Chưa cập nhật');
    }
  }

  // 5. Camera controls
  $('#start-camera-btn').click(async function () {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });

      const video = document.getElementById('camera');
      video.srcObject = stream;
      isCameraActive = true;

      $('#webcam-status').text('Đang hoạt động');
      $('#start-camera-btn').hide();
      $('#stop-camera-btn').show();

      // Enable attendance button if subject is selected
      if (selectedSubject) {
        $('#start-attendance-btn').prop('disabled', false);
      }
    } catch (error) {
      console.error('Error accessing camera:', error);
      $('#webcam-status').text('Lỗi camera');
      showToast('Không thể truy cập camera', 'error');
    }
  });

  $('#stop-camera-btn').click(function () {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }

    const video = document.getElementById('camera');
    video.srcObject = null;
    isCameraActive = false;

    $('#webcam-status').text('Đã tắt');
    $('#start-camera-btn').show();
    $('#stop-camera-btn').hide();
    $('#start-attendance-btn').prop('disabled', true);

    // Stop attendance if active
    if (isAttendanceActive) {
      stopAttendance();
    }
  });

  // 6. Subject selection
  function loadSubjects() {
    $.ajax({
      url: 'http://localhost:8000/api/database/subjects/',
      method: 'GET',
      success: function (response) {
        const select = $('#subject-select');
        select.empty();
        select.append('<option value="" disabled selected>-- Chọn môn học --</option>');

        response.forEach(subject => {
          const teacherName = subject.teacher_name || 'Chưa phân công';
          select.append(`<option value="${subject.id}">${subject.subject_name} - ${teacherName}</option>`);
        });
      },
      error: function (xhr, status, error) {
        console.error('Lỗi khi tải danh sách:', xhr.status);
        showToast('Không thể tải danh sách môn học', 'error');

        // Fallback to mock data
        const subjects = [
          { id: 1, name: 'Lập trình Web', teacher: 'Nguyễn Văn A' },
          { id: 2, name: 'Cơ sở dữ liệu', teacher: 'Trần Thị B' },
          { id: 3, name: 'Lập trình Java', teacher: 'Lê Văn C' }
        ];

        const select = $('#subject-select');
        select.empty();
        select.append('<option value="" disabled selected>-- Chọn môn học --</option>');

        subjects.forEach(subject => {
          select.append(`<option value="${subject.id}">${subject.name} - ${subject.teacher}</option>`);
        });
      }
    });
  }

  $('#subject-select').change(function () {
    const subjectId = $(this).val();
    const subjectText = $(this).find('option:selected').text();

    if (subjectId) {
      selectedSubject = { id: subjectId, name: subjectText };
      $('#selected-subject').text(subjectText);

      // Enable attendance button if camera is active
      if (isCameraActive) {
        $('#start-attendance-btn').prop('disabled', false);
      }
    } else {
      selectedSubject = null;
      $('#selected-subject').text('-- Chọn môn học --');
      $('#start-attendance-btn').prop('disabled', true);
    }
  });

  // 7. Attendance controls
  $('#start-attendance-btn').click(function () {
    if (!selectedSubject || !isCameraActive) {
      showToast('Vui lòng chọn môn học và bật camera', 'warning');
      return;
    }

    startAttendance();
  });

  $('#stop-attendance-btn').click(function () {
    stopAttendance();
  });

  function startAttendance() {
    isAttendanceActive = true;
    $('#attendance-status').text('Đang điểm danh...').removeClass('status-pending status-success status-error').addClass('status-pending');
    $('#start-attendance-btn').hide();
    $('#stop-attendance-btn').show();

    // Simulate face recognition process
    setTimeout(() => {
      const success = Math.random() > 0.3; // 70% success rate
      if (success) {
        completeAttendance(true);
      } else {
        completeAttendance(false);
      }
    }, 3000);
  }

  function stopAttendance() {
    isAttendanceActive = false;
    $('#attendance-status').text('Chưa điểm danh').removeClass('status-pending status-success status-error').addClass('status-pending');
    $('#start-attendance-btn').show();
    $('#stop-attendance-btn').hide();
  }

  function completeAttendance(success) {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('vi-VN');

    if (success) {
      $('#attendance-status').text('Đã điểm danh').removeClass('status-pending status-error').addClass('status-success');
      $('#attendance-time').text(timeStr);
      showToast('Điểm danh thành công!', 'success');

      // Add to history
      addAttendanceRecord(success);

      // Update stats
      loadQuickStats();
    } else {
      $('#attendance-status').text('Điểm danh thất bại').removeClass('status-pending status-success').addClass('status-error');
      showToast('Không nhận diện được khuôn mặt', 'error');
    }

    stopAttendance();
  }

  // 8. Attendance history
  function loadAttendanceHistory() {
    // Mock data - replace with actual API call
    const history = [
      { id: 1, date: '2024-01-15', time: '08:30', subject: 'Lập trình Web', teacher: 'Nguyễn Văn A', status: 'Thành công', accuracy: '95%' },
      { id: 2, date: '2024-01-14', time: '14:00', subject: 'Cơ sở dữ liệu', teacher: 'Trần Thị B', status: 'Thành công', accuracy: '92%' },
      { id: 3, date: '2024-01-13', time: '10:15', subject: 'Lập trình Java', teacher: 'Lê Văn C', status: 'Thất bại', accuracy: '45%' }
    ];

    displayAttendanceHistory(history);
  }

  function displayAttendanceHistory(history) {
    const tbody = $('#attendance-table-body');
    tbody.empty();

    history.forEach((record, index) => {
      const statusClass = record.status === 'Thành công' ? 'status-success' : 'status-error';
      const row = `
        <tr>
          <td>${index + 1}</td>
          <td>${record.date}</td>
          <td>${record.time}</td>
          <td>${record.subject}</td>
          <td>${record.teacher}</td>
          <td><span class="status-badge ${statusClass}">${record.status}</span></td>
          <td>${record.accuracy}</td>
        </tr>
      `;
      tbody.append(row);
    });
  }

  function addAttendanceRecord(success) {
    const now = new Date();
    const dateStr = now.toISOString().split('T')[0];
    const timeStr = now.toLocaleTimeString('vi-VN');

    const record = {
      id: Date.now(),
      date: dateStr,
      time: timeStr,
      subject: selectedSubject.name,
      teacher: selectedSubject.name.split(' - ')[1] || 'N/A',
      status: success ? 'Thành công' : 'Thất bại',
      accuracy: success ? '95%' : '45%'
    };

    // Add to table
    const tbody = $('#attendance-table-body');
    const statusClass = success ? 'status-success' : 'status-error';
    const row = `
      <tr>
        <td>1</td>
        <td>${record.date}</td>
        <td>${record.time}</td>
        <td>${record.subject}</td>
        <td>${record.teacher}</td>
        <td><span class="status-badge ${statusClass}">${record.status}</span></td>
        <td>${record.accuracy}</td>
      </tr>
    `;
    tbody.prepend(row);
  }

  // 9. Quick stats
  function loadQuickStats() {
    // Mock data - replace with actual API call
    const totalAttendance = 15;
    const todayAttendance = 2;

    $('#total-attendance').text(totalAttendance);
    $('#today-attendance').text(todayAttendance);
  }

  // 10. History filters
  $('#date-filter').change(function () {
    filterHistory();
  });

  $('#subject-filter').change(function () {
    filterHistory();
  });

  $('#refresh-history-btn').click(function () {
    loadAttendanceHistory();
    showToast('Đã làm mới dữ liệu', 'success');
  });

  function filterHistory() {
    const dateFilter = $('#date-filter').val();
    const subjectFilter = $('#subject-filter').val();

    // Mock filtering - replace with actual API call
    console.log('Filtering by:', { dateFilter, subjectFilter });
    showToast('Đang lọc dữ liệu...', 'info');
  }

  // 11. Profile actions
  $('#edit-info-btn').click(function () {
    window.location.href = "profile.html";
  });

  // 12. User menu
  $('#userMenuBtn').click(function () {
    $('#userDropdown').toggle();
  });

  $(document).click(function (e) {
    if (!$(e.target).closest('#userMenuBtn, #userDropdown').length) {
      $('#userDropdown').hide();
    }
  });

  // 13. Toast notifications
  function showToast(message, type = 'info') {
    const toast = $(`
      <div class="toast toast-${type}">
        <span>${message}</span>
        <button class="toast-close">&times;</button>
      </div>
    `);

    $('body').append(toast);

    // Auto remove after 3 seconds
    setTimeout(() => {
      toast.remove();
    }, 3000);

    // Manual close
    toast.find('.toast-close').click(function () {
      toast.remove();
    });
  }

  // 14. Initialize
  loadUserData();
  loadSubjects();

  // Auto-start camera on page load (optional)
  // $('#start-camera-btn').click();
});
