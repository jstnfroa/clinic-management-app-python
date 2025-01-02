// Function to open a modal by ID
function openModalById(modalId) {
    document.getElementById(modalId).style.display = 'flex'; // Open the specified modal
}

// Function to close a modal by ID
function closeModalById(modalId) {
    document.getElementById(modalId).style.display = 'none'; // Close the specified modal
}

// Handle form submission for adding staff via AJAX
document.addEventListener('DOMContentLoaded', function() {
    // Open Add Staff Modal
    const openModalBtn = document.getElementById("openModalBtn");
    const staffModal = document.getElementById("staffModal");
    
    if (openModalBtn && staffModal) {
        openModalBtn.addEventListener("click", function() {
            staffModal.style.display = "flex"; // Open the add staff modal
        });
    }

    // Close Modal Function
    function closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = "none"; // Close modal by ID
        }
    }

    // Close staff modal when clicking the close button
    const closeModalBtn = document.getElementById("closeModalBtn");
    if (closeModalBtn) {
        closeModalBtn.addEventListener("click", function() {
            closeModal('staffModal'); // Close the add staff modal
        });
    }

    // Handle form submission for adding staff via AJAX
    const addStaffForm = document.getElementById("addStaffForm");
    if (addStaffForm) {
        addStaffForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent the default form submission
        
            // Gather form data
            const formData = new FormData(addStaffForm);
        
            // Send the form data to the server via AJAX
            fetch("{% url 'user_management' %}", {
                method: "POST",
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
            })
            .then(response => {
                // Check if the response is valid
                if (!response.ok) {
                    throw new Error('Failed to add staff.');
                }
                return response.json(); // Parse the JSON response
            })
            .then(data => {
                console.log("Response data:", data);  // Log response data to see if it matches what you expect
                if (data.message) {
                    alert(data.message); // Success message
                    closeModal('staffModal'); // Close the modal after success
                    // Optionally, refresh the staff list or append the new staff to the table
                } else if (data.error) {
                    alert(data.error); // Show error message
                }
            })
            .catch(error => {
                alert("An error occurred. Please try again.");
                console.error(error);
            });
        });
    }
});

// View Staff Details
function viewStaff(staffId) {
    if (staffId) {
        openModalById("viewStaffModal");

        fetch('/staff/view/' + staffId + '/')
            .then(response => response.json())
            .then(data => {
                if (data.staff) {
                    const staff = data.staff;
                    let staffHtml = `
                        <p><strong>Name:</strong> ${staff.name}</p>
                        <p><strong>Role:</strong> ${staff.role}</p>
                        <p><strong>Email:</strong> ${staff.email_address}</p>
                        <p><strong>Contact Number:</strong> ${staff.contact_number}</p>
                        <p><strong>Status:</strong> ${staff.status}</p>
                        <p><strong>Profile Image:</strong></p>
                        <img src="${staff.profile_image || 'https://via.placeholder.com/40'}" alt="${staff.name}" width="40" height="40" style="border-radius: 50%; margin-top: 10px;">
                    `;
                    document.getElementById("staffDetailsContent").innerHTML = staffHtml;
                } else {
                    Swal.fire(
                        'Error!',
                        'Could not fetch staff details.',
                        'error'
                    );
                }
            })
            .catch(error => {
                console.error('Error fetching staff details:', error);
                Swal.fire(
                    'Error!',
                    'An error occurred while fetching staff details.',
                    'error'
                );
            });
    } else {
        Swal.fire(
            'Error!',
            'Staff ID is undefined.',
            'error'
        );
    }
}

// Edit Staff Details
function editStaff(staffId) {
    openModalById('editStaffModal');

    fetch('/staff/view/' + staffId + '/')
        .then(response => response.json())
        .then(data => {
            if (data.staff) {
                const staff = data.staff;
                document.getElementById('staffId').value = staff.staff_id;
                document.getElementById('name').value = staff.name;
                document.getElementById('role').value = staff.role;
                document.getElementById('email_address').value = staff.email_address;
                document.getElementById('contact_number').value = staff.contact_number;
                document.getElementById('status').value = staff.status;  // Update status field
            }
        })
        .catch(error => {
            console.error('Error fetching staff details:', error);
        });
}

document.addEventListener('DOMContentLoaded', function() {
    // Ensure the form and staffId exist before attaching the event listener
    const editStaffForm = document.getElementById('editStaffForm');
    const staffIdField = document.getElementById('staffId'); // Make sure this field exists in the DOM
    
    if (editStaffForm && staffIdField) {
        editStaffForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission

            const formData = new FormData(editStaffForm); // Get the form data
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value; // Get CSRF token

            const staffId = staffIdField.value; // Get the staff ID from the hidden input field
            if (!staffId) {
                console.error("Staff ID is missing.");
                return;
            }

            // Make the fetch request to update staff
            fetch(`/staff/edit/${staffId}/`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken // Include the CSRF token for security
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Success alert with SweetAlert2
                    Swal.fire(
                        'Success!',
                        'Staff updated successfully!',
                        'success'
                    ).then(() => {
                        // Reload the page only after the alert is closed
                        location.reload();
                    });
                } else {
                    // Error alert with SweetAlert2
                    Swal.fire(
                        'Error!',
                        'Error: ' + data.error,
                        'error'
                    );
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Error alert with SweetAlert2
                Swal.fire(
                    'Error!',
                    'An error occurred. Please try again.',
                    'error'
                );
            });
        });
    } else {
        console.error("editStaffForm or staffId field is missing.");
    }
});


// Function to delete staff
function deleteStaff(staffId) {
    // Show a confirmation dialog using SweetAlert2
    Swal.fire({
        title: 'Are you sure?',
        text: 'This staff member will be deleted permanently.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel',
    }).then(result => {
        if (result.isConfirmed) {
            fetch('/staff/delete/' + staffId + '/', {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    Swal.fire(
                        'Deleted!',
                        'Staff member has been deleted.',
                        'success'
                    ).then(() => {
                        location.reload();
                    });
                } else {
                    Swal.fire(
                        'Error!',
                        'Failed to delete staff member.',
                        'error'
                    );
                }
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire(
                    'Error!',
                    'An error occurred while deleting staff member.',
                    'error'
                );
            });
        }
    });
}
