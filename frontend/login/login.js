// DOM
const loginForm = document.getElementById("inlineLoginForm");
const loginBtn = document.getElementById("loginLink");

loginBtn.onclick = function () {
  const username = document.getElementById("inline-username").value.trim();
  const password = document.getElementById("inline-password").value;

  if (!username || !password) {
    alert("Vui lòng nhập tên đăng nhập và mật khẩu!");
    return;
  }

  const userData = localStorage.getItem("user_" + username);
  if (!userData) {
    alert("Tài khoản không tồn tại!");
    return;
  }

  const user = JSON.parse(userData);
  if (user.password === password) {
    alert("Đăng nhập thành công!");
    localStorage.setItem("currentUser", username);

    if (user.role === "admin") {
      window.location.href = "../admin/admin.html";
    } else {
      window.location.href = "../index/index.html";
    }
  } else {
    alert("Sai mật khẩu!");
  }
};
