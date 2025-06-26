// register.js

document.getElementById("registerForm").addEventListener("submit", async function (e) {
  e.preventDefault();

  const fullName = document.getElementById("registerFullName").value.trim();
  const studentID = document.getElementById("registerStudentID").value.trim();
  const email = document.getElementById("registerName").value.trim();
  const password = document.getElementById("registerPassword").value;
  const confirm = document.getElementById("registerPasswordConfirm").value;

  if (!fullName || !studentID || !email || !password || !confirm) {
    return alert("Vui lòng nhập đầy đủ thông tin.");
  }
  if (password !== confirm) {
    return alert("Mật khẩu xác nhận không khớp.");
  }

  try {
    const res = await fetch("http://localhost:8000/api/user/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + localStorage.getItem("accessToken")
      },
      body: JSON.stringify({
        student_code: studentID,
        full_name: fullName,
        email: email,
        password: password,
        password_confirm: confirm
      })
    });

    if (res.status === 201) {
      alert("Tạo tài khoản thành công!");
      // Quay lại trang Admin hoặc reload để cập nhật danh sách
      window.location.href = "../admin/admin.html";
      // hoặc: window.location.reload();
    } else {
      const err = await res.json();
      const msg = err.non_field_errors?.[0] || err.detail || JSON.stringify(err);
      alert("Lỗi: " + msg);
    }

  } catch (err) {
    console.error(err);
    alert("Không thể kết nối tới server.");
  }
});
