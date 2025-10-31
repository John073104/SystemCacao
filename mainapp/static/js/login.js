document.addEventListener('DOMContentLoaded', function () {
  const loginForm = document.getElementById('login-form');
  const guestButton = document.getElementById('guest-access');

  loginForm.addEventListener('submit', function (e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    firebase.auth().signInWithEmailAndPassword(email, password)
      .then((userCredential) => {
        const user = userCredential.user;

        // Fetch role from Firebase Realtime Database
        return firebase.database().ref('users/' + user.uid).once('value');
      })
      .then((snapshot) => {
        const userData = snapshot.val();
        const role = userData?.role || 'user';

        if (role === 'admin') {
          window.location.href = "/admin/admin_dashboard/";  
        } else {
          window.location.href = "/user/user_dashboard/";
        }
      })
      .catch((error) => {
        displayErrorMessage(error.message);
      });
  });

  guestButton.addEventListener('click', function (e) {
    e.preventDefault();
    window.location.href = "/guest/dashboard/";
  });

  function displayErrorMessage(message) {
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorContainer.classList.remove('hidden');
  }
});
