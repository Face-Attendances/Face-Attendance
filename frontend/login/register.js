document.getElementById("registerForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const username = document.getElementById("registerName").value.trim();
  const password = document.getElementById("registerPassword").value;
  const confirmPassword = document.getElementById("registerPasswordConfirm").value;
  const fullName = document.getElementById("registerFullName").value.trim();
  const studentID = document.getElementById("registerStudentID").value.trim();

  if (!username || !password || !confirmPassword || !fullName || !studentID) {
    alert("Vui lòng nhập đầy đủ thông tin.");
    return;
  }

  if (password !== confirmPassword) {
    alert("Mật khẩu xác nhận không khớp.");
    return;
  }

  if (localStorage.getItem("user_" + username)) {
    alert("Tài khoản đã tồn tại!");
    return;
  }

  const userObj = {
    password,
    fullName,
    studentID,
    phone: "",
    address: "",
    products: [],
    role: username.toLowerCase().includes("admin") ? "admin" : "user"
  };

  localStorage.setItem("user_" + username, JSON.stringify(userObj));
  alert("Đăng ký thành công! Bạn có thể đăng nhập.");
  this.reset(); // Xoá dữ liệu nhập vào
  window.location.href = "login.html";
});
