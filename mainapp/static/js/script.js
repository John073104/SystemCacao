<script>
function showSection(sectionId) {
    // Hide all sections
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.classList.remove('active');
        section.classList.add('hidden'); // Hide all sections
    });
    // Show the selected section
    document.getElementById(sectionId).classList.remove('hidden');
    document.getElementById(sectionId).classList.add('active');

    // Scroll to the top of the section
    const title = document.querySelector(`#${sectionId} h1, #${sectionId} h2`);
    if (title) {
        title.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

function toggleRegister() {
    const loginSection = document.getElementById('login');
    const registerSection = document.getElementById('register');
    if (loginSection.classList.contains('active')) {
        loginSection.classList.remove('active');
        loginSection.classList.add('hidden');
        registerSection.classList.remove('hidden');
        registerSection.classList.add('active');
    } else {
        registerSection.classList.remove('active');
        registerSection.classList.add('hidden');
        loginSection.classList.remove('hidden');
        loginSection.classList.add('active');
    }
}

function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling.querySelector('i');
    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = "password";
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Set the current year in the footer
document.getElementById('current-year').textContent = new Date().getFullYear();
</script>