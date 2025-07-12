// Test authentication script for admin panel
console.log('🔍 Testing authentication...');

// Check if token exists
const token = localStorage.getItem('accessToken');
console.log('Token exists:', !!token);
if (token) {
    console.log('Token preview:', token.substring(0, 50) + '...');
}

// Test API endpoints with authentication
async function testAuth() {
    const API_BASE_URL = 'http://localhost:8000/api';

    // Test 1: GET students (should work without auth)
    console.log('\n📋 Test 1: GET students (no auth required)');
    try {
        const response = await fetch(`${API_BASE_URL}/database/students/`);
        console.log('Status:', response.status);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Success - Found', data.length, 'students');
        } else {
            console.log('❌ Failed:', response.statusText);
        }
    } catch (error) {
        console.log('❌ Error:', error.message);
    }

    // Test 2: POST create student (requires auth)
    console.log('\n👨‍🎓 Test 2: POST create student (requires auth)');
    if (!token) {
        console.log('❌ No token available');
        return;
    }

    try {
        const studentData = {
            student_code: "123456789012",
            name: "Test Student",
            student_class: "TEST-K99",
            dayofbirth: "01/01/2000",
            email: "test@example.com",
            phone_number: "0123456789",
            address: "Test Address"
        };

        const response = await fetch(`${API_BASE_URL}/database/students/create/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(studentData)
        });

        console.log('Status:', response.status);
        const data = await response.json();

        if (response.ok) {
            console.log('✅ Success - Student created');
            console.log('Student ID:', data.id);
        } else {
            console.log('❌ Failed:', data.message || response.statusText);
        }
    } catch (error) {
        console.log('❌ Error:', error.message);
    }

    // Test 3: Login to get fresh token
    console.log('\n🔐 Test 3: Login to get fresh token');
    try {
        const loginData = {
            code: "079205011306",
            password: "Admin@123"
        };

        const response = await fetch(`${API_BASE_URL}/users/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(loginData)
        });

        console.log('Login Status:', response.status);
        const data = await response.json();

        if (response.ok) {
            console.log('✅ Login successful');
            console.log('New token:', data.access.substring(0, 50) + '...');

            // Update token in localStorage
            localStorage.setItem('accessToken', data.access);
            console.log('✅ Token updated in localStorage');
        } else {
            console.log('❌ Login failed:', data.message || response.statusText);
        }
    } catch (error) {
        console.log('❌ Login error:', error.message);
    }
}

// Run tests
testAuth(); 