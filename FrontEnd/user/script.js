$(document).ready(function () {
  // 1. Lấy thông tin user & role
  const currentUser = localStorage.getItem("currentUser");
  const userData = JSON.parse(localStorage.getItem("user_" + currentUser)) || {};
  const role = userData.role || "student";  // 'student' hoặc 'teacher'

  // 2. Xác định API URL dựa vào role
  const apiUrl = (role === "teacher")
    ? "/api/database/teacher-assignments/"      // trả về [{subject_name, class_name}, …]
    : "/api/database/subjects/student/";        // trả về [{subject_name, time}, …]

  // 3. AJAX load dữ liệu vào <select id="subject-select">
  $.ajax({
    url: apiUrl,
    method: 'GET',
    headers: {
      // nếu API cần JWT, mở comment và set token:
      // 'Authorization': 'Bearer ' + localStorage.getItem('accessToken')
    },
    success: function (items) {
      const $sel = $('#subject-select');
      $sel.empty().append('<option value="" disabled selected>-- Chọn môn/lớp --</option>');

      items.forEach(item => {
        let label, value;
        if (role === "teacher") {
          label = `${item.subject_name} – ${item.class_name}`;
          value = `${item.subject_name}|${item.class_name}`;  // hoặc item.id tuỳ bạn
        } else {
          label = `${item.subject_name} (${item.time})`;
          value = item.subject_name;
        }
        $sel.append(
          $('<option>')
            .val(value)
            .text(label)
        );
      });
    },
    error: function (xhr) {
      console.error('Lỗi khi tải danh sách:', xhr.status, xhr.responseText);
      alert('Không thể tải dữ liệu! Mã lỗi: ' + xhr.status);
    }
  });

  // 4. Khi chọn xong, cập nhật hiển thị dưới nút point-in
  $('#subject-select').on('change', function () {
    $('#selected-subject').text($(this).find("option:selected").text());
  });

  // 5. Cập nhật ngày giờ realtime
  function updateDateTime() {
    const now = new Date();
    $('#date').text('Ngày: ' + now.toLocaleDateString('vi-VN'));
    $('#time').text('Giờ: ' + now.toLocaleTimeString('vi-VN'));
    $('#attendance-time').text(now.toLocaleTimeString('vi-VN') + ' - ' + now.toLocaleDateString('vi-VN'));
  }
  updateDateTime();
  setInterval(updateDateTime, 1000);

  // 6. Mở camera
  const video = document.getElementById('camera');
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(err => {
      console.error("Không thể truy cập camera: ", err);
      alert("Không thể truy cập camera. Hãy kiểm tra quyền trình duyệt.");
    });

  // 7. Xử lý nút Điểm danh
  $('#check-in-btn').click(function () {
    const name = $('#student-name').text();
    const mssv = $('#student-id').text();
    const subjectText = $('#subject-select option:selected').text();
    if (!subjectText) {
      alert("Vui lòng chọn môn/học phần trước khi điểm danh.");
      return;
    }
    const now = new Date();
    const time = now.toLocaleTimeString('vi-VN');
    const date = now.toLocaleDateString('vi-VN');
    const rowNo = $('#attendance-table-body tr').length + 1;

    const newRow = `
      <tr>
        <td>${rowNo}</td>
        <td>${name}</td>
        <td>${mssv}</td>
        <td>${subjectText}</td>
        <td>✅ Đã điểm danh</td>
        <td>${time}</td>
      </tr>`;
    $('#attendance-table-body').append(newRow);
    $('#attendance-time').text(time + ' - ' + date);
    $('#selected-subject').text(subjectText);
  });

  // 8. Xử lý Lịch sử điểm danh (ẩn/hiện phần mở rộng)
  let isExpanded = false;
  $('#toggle-more-btn').click(function () {
    $('#more-info').slideToggle();
    $(this).text(isExpanded ? " Xem thêm" : " Thu gọn");
    isExpanded = !isExpanded;
  });

  // 9. Chuyển sang profile.html khi bấm sửa thông tin
  $('#edit-info-btn').click(() => {
    window.location.href = "profile.html";
  });

  // 10. Hiện/ẩn dropdown user menu
  $('#userMenuBtn').click(() => $('#userDropdown').toggle());
  $(document).click(e => {
    if (!$(e.target).closest('#userMenuBtn, #userDropdown').length) {
      $('#userDropdown').hide();
    }
  });

  // 11. Điền thông tin profile trên UI
  if (userData) {
    $('#student-name').text(userData.fullName || 'Chưa cập nhật');
    $('#student-id').text(userData.studentID || 'Chưa cập nhật');
    $('#student-class').text(userData.class || 'Chưa cập nhật');
    $('#student-course').text(userData.course || 'Chưa cập nhật');
    $('#student-dob').text(userData.dob || 'Chưa cập nhật');
    $('#student-email').text(userData.email || 'Chưa cập nhật');
    $('#student-phone').text(userData.phone || 'Chưa cập nhật');
    $('#student-address').text(userData.address || 'Chưa cập nhật');
  }
});
