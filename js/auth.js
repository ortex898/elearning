
async function signup(email, password, userType) {
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password, userType })
        });
        
        const data = await response.json();
        if (!response.ok) {
            alert(data.error);
            return false;
        }
        
        localStorage.setItem('currentUser', JSON.stringify(data));
        return true;
    } catch (error) {
        alert('Registration failed');
        return false;
    }
}

async function login(email, password) {
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        if (!response.ok) {
            alert(data.error);
            return false;
        }
        
        localStorage.setItem('currentUser', JSON.stringify(data));
        return data;
    } catch (error) {
        alert('Login failed');
        return false;
    }
}

function updateProfile(profileData) {
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    const userIndex = users.findIndex(u => u.email === currentUser.email);
    
    if (userIndex !== -1) {
        users[userIndex].profile = {...users[userIndex].profile, ...profileData};
        users[userIndex].isProfileComplete = true;
        localStorage.setItem('users', JSON.stringify(users));
        localStorage.setItem('currentUser', JSON.stringify(users[userIndex]));
        return true;
    }
    return false;
}

function getCurrentUser() {
    return JSON.parse(localStorage.getItem('currentUser'));
}

function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = 'index.html';
}
