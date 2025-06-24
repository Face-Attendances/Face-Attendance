$(document).ready(function () {
  // Cập nhật ngày giờ
  function updateDateTime() {
    const now = new Date();
    const dateStr = now.toLocaleDateString('vi-VN');
    const timeStr = now.toLocaleTimeString('vi-VN');
    $('#date').text('Ngày: ' + dateStr);
    $('#time').text('Giờ: ' + timeStr);
    $('#attendance-time').text(timeStr + ' - ' + dateStr);
  }

  updateDateTime();
  setInterval(updateDateTime, 1000);

  // Mở camera
  const video = document.getElementById('camera');
  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      video.srcObject = stream;
    })
    .catch(error => {
      console.error("Không thể truy cập camera: ", error);
      alert("Không thể truy cập camera. Hãy kiểm tra quyền trình duyệt.");
    });

  // Load thông tin user từ localStorage
  const currentUser = localStorage.getItem("currentUser");
  const userData = JSON.parse(localStorage.getItem("user_" + currentUser));
  if (userData) {
    $('#student-name').text(userData.fullName || '...');
    $('#student-id').text(userData.studentID || '...');
    $('#student-phone').text(userData.phone || 'Chưa cập nhật');
    $('#student-address').text(userData.address || 'Chưa cập nhật');
    $('#student-email').text(userData.email || 'Chưa cập nhật');
    $('#student-dob').text(userData.dob || 'Chưa cập nhật');
  }

  // Xử lý chọn môn học
  $('#subject-select').on('change', function () {
    const selected = $(this).find("option:selected").text();
    $('#selected-subject').text(selected);
  });

  // Xử lý nút Điểm danh
  $('#check-in-btn').click(function () {
    const name = $('#student-name').text();
    const mssv = $('#student-id').text();
    const subject = $('#subject-select').val();
    const subjectText = $('#subject-select option:selected').text();
    const now = new Date();
    const timeStr = now.toLocaleTimeString('vi-VN');
    const dateStr = now.toLocaleDateString('vi-VN');

    if (!subject) {
      alert("Vui lòng chọn môn học trước khi điểm danh.");
      return;
    }

    const rowCount = $('#attendance-table-body tr').length + 1;
    const newRow = `
      <tr>
        <td>${rowCount}</td>
        <td>${name}</td>
        <td>${mssv}</td>
        <td>${subjectText}</td>
        <td>✅ Đã điểm danh</td>
        <td>${timeStr}</td>
      </tr>
    `;
    $('#attendance-table-body').append(newRow);

    $('#attendance-time').text(timeStr + ' - ' + dateStr);
    $('#selected-subject').text(subjectText);
  });
  // Xử lý nút Lịch sử điểm danh// Nút "Xem thêm" để ẩn/hiện phần mở rộng
 let isExpanded = false;
 $('#toggle-more-btn').click(function () {
  if (isExpanded) {
    $('#more-info').slideUp();
    $(this).text(" Xem thêm");
  } else {
    $('#more-info').slideDown();
    $(this).text(" Thu gọn");
  }
  isExpanded = !isExpanded;
 });

 // Nút chỉnh sửa → chuyển sang trang profile.html
 $('#edit-info-btn').click(function () {
  window.location.href = "profile.html";
  });


  // Hiện/ẩn dropdown khi bấm vào nút
 $('#userMenuBtn').click(function () {
  $('#userDropdown').toggle();
 });

 // Ẩn dropdown khi click ra ngoài
 $(document).click(function (e) {
  if (!$(e.target).closest('#userMenuBtn, #userDropdown').length) {
    $('#userDropdown').hide();
  }

  const currentUser = localStorage.getItem("currentUser");
  const userData = JSON.parse(localStorage.getItem("user_" + currentUser));

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
});

