document.addEventListener('DOMContentLoaded', function() {
  // Edit Profile Modal
  var editProfileModal = document.getElementById('edit-profile-modal');
  var editProfileBtn = document.getElementById('edit-profile-btn');
  var closeEditProfileModal = document.getElementById('close-modal');

  // Change Password Modal
  var changePasswordModal = document.getElementById('change-password-modal');
  var changePasswordBtn = document.getElementById('change-password-btn');  // Ensure correct id
  var closeChangePasswordModal = document.getElementById('close-change-password-modal');

  // Show Edit Profile Modal
  editProfileBtn.onclick = function() {
      editProfileModal.style.display = 'block';
  }

  // Close Edit Profile Modal
  closeEditProfileModal.onclick = function() {
      editProfileModal.style.display = 'none';
  }

  // Show Change Password Modal
  changePasswordBtn.onclick = function() {
      changePasswordModal.style.display = 'block';
  }

  // Close Change Password Modal
  closeChangePasswordModal.onclick = function() {
      changePasswordModal.style.display = 'none';
  }

  // Close modals when clicking outside
  window.onclick = function(event) {
      if (event.target == editProfileModal) {
          editProfileModal.style.display = 'none';
      }
      if (event.target == changePasswordModal) {
          changePasswordModal.style.display = 'none';
      }
  }

  // Show/Hide Password Functionality
  function togglePasswordVisibility(inputId, toggleId) {
      var inputField = document.getElementById(inputId);
      var toggleIcon = document.getElementById(toggleId);
      toggleIcon.onclick = function() {
          // Toggle between password and text input type
          if (inputField.type === "password") {
              inputField.type = "text";
          } else {
              inputField.type = "password";
          }
      }
  }

  // Toggle password visibility for each field
  togglePasswordVisibility('old_password', 'show-old-password');
  togglePasswordVisibility('new_password', 'show-new-password');
  togglePasswordVisibility('confirm_password', 'show-confirm-password');
});
