// Theme Toggle
function toggleTheme() {
    document.body.classList.toggle('dark');
    const isDark = document.body.classList.contains('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
    const themeIcon = document.querySelector('.theme-icon');
    if (themeIcon) {
        themeIcon.textContent = isDark ? '☀️' : '🌙';
    }
}

// Load saved theme
document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark');
    }
    updateThemeIcon(savedTheme === 'dark');

    // Add loaded class for animation
    setTimeout(() => {
        document.body.classList.add('loaded');
    }, 100);
});

// Page Transition with Animation
function navigateWithAnimation(url, delay = 500) {
    const body = document.body;
    const card = document.querySelector('.auth-card');

    if (card) {
        card.classList.add('slide-out');
    }

    body.classList.add('page-transition');

    setTimeout(() => {
        window.location.href = url;
    }, delay);
}

// Phone Number Formatting
function formatPhoneNumber(input) {
    let value = input.value.replace(/\D/g, '');
    if (value.startsWith('0')) {
        value = value.substring(0, 11);
    } else if (value.startsWith('98')) {
        value = '0' + value.substring(2);
    }
    input.value = value;
}

// Show Message
function showMessage(text, type = 'info') {
    const messagesContainer = document.getElementById('messagesContainer');
    if (!messagesContainer) return;

    const message = document.createElement('div');
    message.className = `message ${type}`;

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    message.innerHTML = `
        <span>${icons[type] || icons.info}</span>
        <span>${text}</span>
    `;

    messagesContainer.appendChild(message);

    // Auto remove after 5 seconds
    setTimeout(() => {
        message.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => {
            message.remove();
        }, 300);
    }, 5000);
}

// Add slideOut animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);

// Signup Form Handler
const signupForm = document.getElementById('signupForm');
if (signupForm) {
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    }

    signupForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const fullname = document.getElementById('fullname').value.trim();
        const phone = document.getElementById('phone').value.trim();

        // Validation
        if (!fullname || fullname.length < 3) {
            showMessage('نام کامل باید حداقل 3 کاراکتر باشد!', 'error');
            return;
        }

        if (!phone || phone.length !== 11 || !phone.match(/^09[0-9]{9}$/)) {
            showMessage('شماره تلفن معتبر نیست! شماره باید 11 رقمی و با 09 شروع شود.', 'error');
            return;
        }

        // Save to sessionStorage
        sessionStorage.setItem('signupPhone', phone);
        sessionStorage.setItem('signupFullname', fullname);

        // Show success message
        showMessage('کد تأیید در حال ارسال است...', 'info');

        // Navigate to verify page with animation
        setTimeout(() => {
            navigateWithAnimation('verify.html', 800);
        }, 500);
    });
}

// Verify Page Handler
document.addEventListener('DOMContentLoaded', function() {
    const phoneNumber = sessionStorage.getItem('signupPhone');
    const phoneDisplay = document.getElementById('phoneNumber');

    if (phoneDisplay && phoneNumber) {
        // Format phone for display
        const formatted = phoneNumber.replace(/(\d{4})(\d{3})(\d{4})/, '$1 $2 $3');
        phoneDisplay.textContent = formatted;
    } else if (phoneDisplay) {
        // If no phone in session, redirect to signup
        navigateWithAnimation('signup.html', 300);
    }

    // Code Inputs Handler
    const codeInputs = document.querySelectorAll('.code-input');
    if (codeInputs.length > 0) {
        codeInputs.forEach((input, index) => {
            input.addEventListener('input', function(e) {
                const value = e.target.value.replace(/\D/g, '');
                e.target.value = value;

                if (value && index < codeInputs.length - 1) {
                    codeInputs[index + 1].focus();
                }

                if (value) {
                    e.target.classList.add('filled');
                } else {
                    e.target.classList.remove('filled');
                }
            });

            input.addEventListener('keydown', function(e) {
                if (e.key === 'Backspace' && !e.target.value && index > 0) {
                    codeInputs[index - 1].focus();
                }
            });

            input.addEventListener('paste', function(e) {
                e.preventDefault();
                const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
                pastedData.split('').forEach((char, i) => {
                    if (codeInputs[i]) {
                        codeInputs[i].value = char;
                        codeInputs[i].classList.add('filled');
                    }
                });
                codeInputs[Math.min(pastedData.length, codeInputs.length - 1)].focus();
            });
        });

        // Focus first input
        codeInputs[0].focus();

        // Start countdown
        startCountdown('countdown', 120);
    }

    // Verify Form Handler
    const verifyForm = document.getElementById('verifyForm');
    if (verifyForm) {
        verifyForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const codeInputs = document.querySelectorAll('.code-input');
            const code = Array.from(codeInputs).map(input => input.value).join('');

            if (code.length !== 6) {
                showMessage('لطفاً کد 6 رقمی را کامل وارد کنید!', 'error');
                return;
            }

            // Simulate API call
            showMessage('در حال تأیید کد...', 'info');

            setTimeout(() => {
                showMessage('حساب کاربری شما با موفقیت ایجاد شد!', 'success');
                // Clear session storage
                sessionStorage.removeItem('signupPhone');
                sessionStorage.removeItem('signupFullname');

                // Redirect to login or dashboard
                setTimeout(() => {
                    navigateWithAnimation('login.html', 1000);
                }, 1500);
            }, 1000);
        });
    }
});

// Login Form Handler - Phone Step
const loginPhoneForm = document.getElementById('loginPhoneForm');
if (loginPhoneForm) {
    const phoneInput = document.getElementById('loginPhone');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            formatPhoneNumber(this);
        });
    }

    loginPhoneForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const phone = document.getElementById('loginPhone').value.trim();

        if (!phone || phone.length !== 11 || !phone.match(/^09[0-9]{9}$/)) {
            showMessage('شماره تلفن معتبر نیست!', 'error');
            return;
        }

        // Save to sessionStorage
        sessionStorage.setItem('loginPhone', phone);

        // Hide phone form, show code form
        loginPhoneForm.style.display = 'none';
        loginPhoneForm.classList.add('hidden');

        const codeForm = document.getElementById('loginCodeForm');
        if (codeForm) {
            codeForm.style.display = 'block';
            codeForm.classList.add('slide-in');
        }

        showMessage('کد تأیید ارسال شد!', 'success');

        // Start countdown
        startCountdown('loginCountdown', 120);

        // Focus code input
        const codeInput = document.getElementById('loginCode');
        if (codeInput) {
            setTimeout(() => codeInput.focus(), 300);
        }
    });
}

// Login Form Handler - Code Step
const loginCodeForm = document.getElementById('loginCodeForm');
if (loginCodeForm) {
    const codeInput = document.getElementById('loginCode');
    if (codeInput) {
        codeInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.replace(/\D/g, '').slice(0, 6);
        });
    }

    loginCodeForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const code = document.getElementById('loginCode').value.trim();

        if (code.length !== 6) {
            showMessage('کد باید 6 رقمی باشد!', 'error');
            return;
        }

        // Simulate API call
        showMessage('در حال ورود...', 'info');

        setTimeout(() => {
            showMessage('با موفقیت وارد شدید!', 'success');
            sessionStorage.removeItem('loginPhone');

            // Redirect to dashboard or home
            setTimeout(() => {
                // navigateWithAnimation('dashboard.html', 1000);
                console.log('Login successful!');
            }, 1500);
        }, 1000);
    });
}

// Resend Code Function
function resendCode(type) {
    const countdownId = type === 'login' ? 'loginCountdown' : 'countdown';
    const resendBtnId = type === 'login' ? 'resendLoginCode' : 'resendCode';

    showMessage('کد تأیید مجدداً ارسال شد!', 'success');

    // Start countdown again
    startCountdown(countdownId, 120);
}

// Countdown Timer
function startCountdown(elementId, seconds) {
    const countdownElement = document.getElementById(elementId);
    if (!countdownElement) return;

    const resendBtnId = elementId === 'loginCountdown' ? 'resendLoginCode' : 'resendCode';
    const resendBtn = document.getElementById(resendBtnId);

    if (resendBtn) {
        resendBtn.disabled = true;
    }

    let remaining = seconds;

    const updateCountdown = () => {
        const minutes = Math.floor(remaining / 60);
        const secs = remaining % 60;
        countdownElement.textContent = `${minutes}:${secs.toString().padStart(2, '0')} باقی مانده`;

        if (remaining > 0) {
            remaining--;
            setTimeout(updateCountdown, 1000);
        } else {
            countdownElement.textContent = '';
            if (resendBtn) {
                resendBtn.disabled = false;
            }
        }
    };

    updateCountdown();
}

// Form Input Animations
document.querySelectorAll('.form-group input').forEach(input => {
    input.addEventListener('focus', function() {
        this.parentElement.style.transform = 'scale(1.02)';
    });

    input.addEventListener('blur', function() {
        this.parentElement.style.transform = 'scale(1)';
    });
});

// Smooth scroll to top on page load
window.addEventListener('load', function() {
    window.scrollTo(0, 0);
});
