// ============================================
// FilmCollab — Form Validation (validate.js)
// Simple, beginner-friendly JavaScript
// ============================================

// ── Helper: Show error message ──
function showError(elementId, message) {
    var el = document.getElementById(elementId);
    if (el) el.textContent = message;
}

// ── Helper: Clear error message ──
function clearError(elementId) {
    var el = document.getElementById(elementId);
    if (el) el.textContent = '';
}

// ── Helper: Check if a string is a valid email ──
function isValidEmail(email) {
    return email.includes('@') && email.includes('.');
}


// ════════════════════════════════════
// Register Form Validation
// ════════════════════════════════════
var registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', function (event) {
        var isValid = true;

        // Clear previous errors
        clearError('usernameError');
        clearError('emailError');
        clearError('passwordError');

        var username = document.getElementById('username').value.trim();
        var email    = document.getElementById('email').value.trim();
        var password = document.getElementById('password').value;

        // Validate username
        if (username.length < 3) {
            showError('usernameError', 'Username must be at least 3 characters.');
            isValid = false;
        }

        // Validate email
        if (!isValidEmail(email)) {
            showError('emailError', 'Please enter a valid email address.');
            isValid = false;
        }

        // Validate password
        if (password.length < 6) {
            showError('passwordError', 'Password must be at least 6 characters.');
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault(); // Stop form from submitting
        }
    });
}


// ════════════════════════════════════
// Login Form Validation
// ════════════════════════════════════
var loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
        var isValid = true;

        clearError('usernameError');
        clearError('passwordError');

        var username = document.getElementById('username').value.trim();
        var password = document.getElementById('password').value;

        if (username.length === 0) {
            showError('usernameError', 'Please enter your username.');
            isValid = false;
        }

        if (password.length === 0) {
            showError('passwordError', 'Please enter your password.');
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
}


// ════════════════════════════════════
// Project Form Validation
// ════════════════════════════════════
var projectForm = document.getElementById('projectForm');
if (projectForm) {
    projectForm.addEventListener('submit', function (event) {
        var isValid = true;

        clearError('titleError');
        clearError('genreError');

        var title = document.getElementById('title').value.trim();
        var genre = document.getElementById('genre').value;

        if (title.length < 2) {
            showError('titleError', 'Project title must be at least 2 characters.');
            isValid = false;
        }

        if (genre === '' || genre === '-- Select a genre --') {
            showError('genreError', 'Please select a genre.');
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
}


// ════════════════════════════════════
// Aspect Form Validation
// ════════════════════════════════════
var aspectForm = document.getElementById('aspectForm');
if (aspectForm) {
    aspectForm.addEventListener('submit', function (event) {
        var isValid = true;

        clearError('aspectError');
        clearError('detailsError');

        var aspectType = document.getElementById('aspect_type').value;
        var details    = document.getElementById('details').value.trim();

        if (aspectType === '' || aspectType === '-- Select aspect type --') {
            showError('aspectError', 'Please select an aspect type.');
            isValid = false;
        }

        if (details.length < 5) {
            showError('detailsError', 'Please provide more details (at least 5 characters).');
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
}
