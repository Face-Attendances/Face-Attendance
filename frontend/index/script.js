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

  // Xử lý chọn môn học
  $('#subject-select').on('change', function () {
    const selected = $(this).find("option:selected").text();
    $('#selected-subject').text(selected);
  });
});
