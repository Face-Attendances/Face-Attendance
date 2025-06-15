
$(document).ready(function () {
  $('#registerLink').click(function () {
    const modal = new bootstrap.Modal(document.getElementById('registerModal'));
    modal.show();
  });

  $('#registerClose, #registerCloseFooter').click(function () {
    const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
    modal.hide();
  });
    // Cảnh báo lắc form nếu thiếu dữ liệu
  $('#loginLink').click(function () {
    const user = $('#inline-username').val().trim();
    const pass = $('#inline-password').val();
    if (!user || !pass) {
      $('.card').addClass('shake');
      setTimeout(() => $('.card').removeClass('shake'), 500);
    }
  });
});
