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
    } else if (user.role === "teacher") 
      {
      window.location.href = "../user/user_gv/user_gv.html";
    } else if (user.role === "student") {
      window.location.href = "../user/user.html";
    } else {
      alert("Vai trò người dùng không hợp lệ!");
    }
  } else {
    alert("Sai mật khẩu!");
  }
};
