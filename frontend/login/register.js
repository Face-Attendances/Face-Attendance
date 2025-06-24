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

  // Xét vai trò tự động dựa theo username
  let role = "student"; // mặc định
  const lower = username.toLowerCase();
  if (lower === "admin") {
    role = "admin";
  } else if (lower.includes("gv") || lower.includes("teacher")) {
    role = "teacher";
  }

  const userObj = {
    username,
    password,
    fullName,
    studentID,
    role,
    phone: "",
    address: "",
    products: []
  };

  localStorage.setItem("user_" + username, JSON.stringify(userObj));
  alert("Đăng ký thành công với vai trò: " + role.toUpperCase());
  this.reset();
  window.location.href = "login.html";
});
