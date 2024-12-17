document.addEventListener('DOMContentLoaded', function() {
    const signInButton = document.getElementById('signIn');
    const signUpButton = document.getElementById('signUp');
    const container = document.getElementById('container');

    signInButton.addEventListener('click', () => {
        container.classList.remove('right-panel-active');
    });

    signUpButton.addEventListener('click', () => {
        container.classList.add('right-panel-active');
    });

    document.getElementById('signInForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const email = document.querySelector('#signInForm input[type="email"]').value;
        const password = document.querySelector('#signInForm input[type="password"]').value;

        const response = await fetch('http://localhost:8000/login', {  // 确保路径正确
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (data.status === 'success') {
            window.location.href = data.redirect;
        } else {
            alert(data.message);
        }
    });

    document.getElementById('signUpForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const username = document.querySelector('#signUpForm input[type="text"]').value;
        const email = document.querySelector('#signUpForm input[type="email"]').value;
        const password = document.querySelector('#signUpForm input[type="password"]').value;

        const response = await fetch('http://localhost:8000/register', {  // 确保路径正确
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await response.json();

        if (data.status === 'success') {
            alert('Registration successful, please log in.');
            container.classList.remove('right-panel-active');
        } else {
            alert(data.message);
        }
    });
});
