document.addEventListener('DOMContentLoaded', function () {
    // Modals and Buttons
    const editProfileModal = document.getElementById('edit-profile-modal');
    const editProfileBtn = document.getElementById('edit-profile-btn');
    const closeEditProfileModal = document.getElementById('close-modal');

    const changePasswordModal = document.getElementById('change-password-modal');
    const changePasswordBtn = document.getElementById('change-password-btn');
    const closeChangePasswordModal = document.getElementById('close-change-password-modal');

    // Profile image update
    const profileImageWrapper = document.querySelector('.profile-image-wrapper');
    const profileImage = document.getElementById('profile-image');
    const profileImageInput = document.getElementById('profile-image-input');

    // Show/Hide Modal Logic
    function showModal(modal) {
        modal.style.display = 'block';
    }

    function closeModal(modal) {
        modal.style.display = 'none';
    }

    // Event Listeners for Modals
    editProfileBtn.onclick = () => showModal(editProfileModal);
    closeEditProfileModal.onclick = () => closeModal(editProfileModal);

    changePasswordBtn.onclick = () => showModal(changePasswordModal);
    closeChangePasswordModal.onclick = () => closeModal(changePasswordModal);

    // Close modals when clicking outside of them
    window.onclick = function (event) {
        if (event.target === editProfileModal) closeModal(editProfileModal);
        if (event.target === changePasswordModal) closeModal(changePasswordModal);
    };

    // Show/Hide Password Functionality
    function togglePasswordVisibility(inputId, toggleId) {
        const inputField = document.getElementById(inputId);
        const toggleIcon = document.getElementById(toggleId);

        toggleIcon.onclick = function () {
            if (inputField.type === 'password') {
                inputField.type = 'text';
                toggleIcon.textContent = '🙈'; // Icon for hidden state
            } else {
                inputField.type = 'password';
                toggleIcon.textContent = '👁️'; // Icon for visible state
            }
        };
    }

    // Apply toggle functionality to password fields
    togglePasswordVisibility('old_password', 'show-old-password');
    togglePasswordVisibility('new_password', 'show-new-password');
    togglePasswordVisibility('confirm_password', 'show-confirm-password');

    // Form Submission Handling
    const editProfileForm = document.getElementById('edit-profile-form');
    const changePasswordForm = document.getElementById('change-password-form');

    editProfileForm.onsubmit = function (event) {
        // Add any custom validation logic here
        const fullName = document.getElementById('full_name').value;
        const email = document.getElementById('email').value;

        if (!fullName || !email) {
            event.preventDefault(); // Prevent form submission
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: 'Please fill in all required fields.',
            });
        }
    };

    changePasswordForm.onsubmit = function (event) {
        // Add password validation logic
        const newPassword = document.getElementById('new_password').value;
        const confirmPassword = document.getElementById('confirm_password').value;

        if (newPassword !== confirmPassword) {
            event.preventDefault(); // Prevent form submission
            Swal.fire({
                icon: 'error',
                title: 'Oops...',
                text: 'New passwords do not match.',
            });
        }
    };

    // Profile Image Upload Logic
    profileImageWrapper.addEventListener('click', function () {
        profileImageInput.click(); // Trigger file input when profile image is clicked
    });

    profileImageInput.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                profileImage.src = e.target.result; // Update the profile image preview
            };
            reader.readAsDataURL(file);

            // Send the image file to the server for profile update
            const formData = new FormData();
            formData.append('profile_image', file);

            // Make sure to include CSRF token in the request
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch('/update-profile-image/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken // CSRF protection
                },
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        Swal.fire({
                            icon: 'success',
                            title: 'Success!',
                            text: 'Profile image updated successfully!',
                        });
                    } else {
                        Swal.fire({
                            icon: 'error',
                            title: 'Error!',
                            text: 'Error updating profile image.',
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    Swal.fire({
                        icon: 'error',
                        title: 'Error!',
                        text: 'An error occurred while updating your profile image.',
                    });
                });
        }
    });
});
