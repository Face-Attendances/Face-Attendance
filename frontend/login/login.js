// login.js

// chỉ chạy khi toàn bộ DOM đã load (defer hoặc DOMContentLoaded)
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('loginLink');
  btn.addEventListener('click', async e => {
    e.preventDefault();

    const code = document
      .getElementById('inline-username')
      .value.trim();
    const password = document
      .getElementById('inline-password')
      .value;

    if (!code || !password) {
      return alert('Vui lòng nhập mã số và mật khẩu');
    }

    // Validate code format (12 digits)
    if (!/^\d{12}$/.test(code)) {
      return alert('Mã số phải có đúng 12 chữ số');
    }

    try {
      const res = await fetch('http://localhost:8000/api/users/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, password })
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        const errorMessage = err.non_field_errors ? err.non_field_errors[0] : (err.detail || 'Đăng nhập thất bại');
        return alert(errorMessage);
      }

      const { access, refresh, role } = await res.json();
      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);
      localStorage.setItem('currentRole', role);

      // redirect
      if (role === 'admin') {
        // từ login.html nhảy lên folder cha, rồi vào admin/admin.html
        window.location.href = '../admin/admin.html';
      }
      else if (role === 'teacher') {
        // từ login.html nhảy lên folder cha, rồi vào user/user_gv/user_gv.html
        window.location.href = '../user/user_gv/user_gv.html';
      }
      else {
        // student: vào user/user.html
        window.location.href = '../user/user.html';
      }

    } catch (err) {
      console.error(err);
      alert('Không thể kết nối tới server.');
    }
  });
});
