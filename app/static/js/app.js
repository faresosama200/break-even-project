/**
 * SmartBEP — Main JavaScript
 * Theme toggle, navigation, dropdown, utilities
 */

document.addEventListener('DOMContentLoaded', function () {

    // === Theme Toggle ===
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    const stored = localStorage.getItem('theme');

    if (stored) {
        html.setAttribute('data-theme', stored);
    } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        html.setAttribute('data-theme', 'dark');
    }
    updateThemeIcon();

    if (themeToggle) {
        themeToggle.addEventListener('click', function () {
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            updateThemeIcon();
        });
    }

    function updateThemeIcon() {
        if (!themeToggle) return;
        const icon = themeToggle.querySelector('i');
        if (html.getAttribute('data-theme') === 'dark') {
            icon.className = 'fas fa-sun';
        } else {
            icon.className = 'fas fa-moon';
        }
    }

    // === Mobile Nav Toggle ===
    const navToggle = document.getElementById('nav-toggle');
    const navbar = document.querySelector('.navbar');
    if (navToggle) {
        navToggle.addEventListener('click', function () {
            navbar.classList.toggle('nav-open');
        });
    }

    // === Dropdown Toggle ===
    document.querySelectorAll('.dropdown-toggle').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.stopPropagation();
            const dd = btn.closest('.dropdown');
            dd.classList.toggle('open');
        });
    });
    document.addEventListener('click', function () {
        document.querySelectorAll('.dropdown.open').forEach(function (dd) {
            dd.classList.remove('open');
        });
    });

    // === Auto-dismiss flash messages ===
    document.querySelectorAll('.alert').forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function () { alert.remove(); }, 300);
        }, 5000);
    });

    // === Form validation enhancement ===
    document.querySelectorAll('.project-form').forEach(function (form) {
        form.addEventListener('submit', function (e) {
            let valid = true;
            form.querySelectorAll('[required]').forEach(function (input) {
                if (!input.value.trim()) {
                    input.classList.add('is-invalid');
                    valid = false;
                } else {
                    input.classList.remove('is-invalid');
                }
            });
            if (!valid) {
                e.preventDefault();
                const first = form.querySelector('.is-invalid');
                if (first) first.focus();
            }
        });
    });

    // === Number formatting ===
    window.formatNumber = function (num, decimals) {
        decimals = decimals !== undefined ? decimals : 0;
        return Number(num).toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals,
        });
    };

});
