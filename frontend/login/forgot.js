document.addEventListener("DOMContentLoaded", function () {
  const forgotForm = document.getElementById("forgotForm");

  forgotForm.addEventListener("submit", function (e) {
    e.preventDefault(); // Ngăn reload lại trang

    const emailInput = document.getElementById("email");
    const email = emailInput.value.trim();

    if (email === "") {
      alert("❗ Vui lòng nhập Email hoặc MSSV.");
      emailInput.focus();
      return;
    }

    // Giả lập gửi liên kết khôi phục mật khẩu
    alert("✅ Đã gửi liên kết đặt lại mật khẩu đến: " + email);

    // Reset form
    forgotForm.reset();
  });
});
