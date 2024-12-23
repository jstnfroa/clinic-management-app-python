// Get the modal for adding staff
var modal = document.getElementById('staffModal');

// Get the button that opens the modal
var openModalBtn = document.getElementById('openModalBtn');

// Get the <span> element that closes the modal
var closeModalBtn = document.getElementById('closeModalBtn');

// Get the form for adding staff
const addStaffForm = document.getElementById('addStaffForm');

// Handle the opening of the modal
openModalBtn.onclick = function() {
    modal.style.display = 'block';
}

// Generalized function to close the modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';  // Close the specified modal
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    var modals = document.querySelectorAll('.modal');
    modals.forEach(function(modal) {
        if (event.target === modal) {
            closeModal(modal.id);  // Close the modal if clicked outside of it
        }
    });
}


// Handle form submission for adding staff
addStaffForm.addEventListener('submit', function(e) {
    e.preventDefault();  // Prevent default form submission

    const formData = new FormData(addStaffForm);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch(userManagementUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: data.message,
            });
            modal.style.display = 'none';  // Close the modal after success
        } else {
            Swal.fire({
                icon: 'error',
                title: 'Error!',
                text: data.error,
            });
        }
    })
    .catch(error => {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error!',
            text: 'An error occurred. Please try again.',
        });
    });
});

// Function to open a modal by ID
function openModalById(modalId) {
    document.getElementById(modalId).style.display = 'block';  // Open the specified modal
}

// Function to close any modal
function closeModalById(modalId) {
    document.getElementById(modalId).style.display = 'none';  // Close the specified modal
}

// Function to view staff details
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

// Function to edit staff details
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
            }
        })
        .catch(error => {
            console.error('Error fetching staff details:', error);
        });
}

// Handle form submission for editing staff details
document.getElementById('editStaffForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/staff/edit/' + document.getElementById('staffId').value + '/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
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
            );
            closeModalById('editStaffModal');
            location.reload();
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

function deleteStaff(staffId) {
    // Show a confirmation dialog using SweetAlert2
    Swal.fire({
        title: 'Are you sure?',
        text: 'This staff member will be deleted permanently.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'No, cancel'
    }).then((result) => {
        if (result.isConfirmed) {
            // Log the CSRF token for debugging
            console.log('CSRF Token:', getCookie('csrftoken'));

            // Make an AJAX request to delete the staff
            fetch(`/delete_staff/${staffId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')  // Ensure the CSRF token is included
                },
                body: JSON.stringify({})  // Empty body as no data is needed
            })
            .then(response => {
                console.log('Response:', response);  // Log the whole response object
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.statusText}`);
                }
                return response.json();  // Parse the JSON response
            })
            .then(data => {
                console.log('Data:', data);  // Log the response data
                if (data.status === 'success') {
                    // Success alert with SweetAlert2
                    Swal.fire(
                        'Deleted!',
                        'Staff member deleted successfully.',
                        'success'
                    );

                    // Check if the staff row exists before removing it
                    const staffRow = document.getElementById(`staff-row-${staffId}`);
                    console.log('Staff Row:', staffRow);  // Check if the element exists
                    if (staffRow) {
                        staffRow.remove();  // Only remove if it exists
                    } else {
                        console.error(`Staff row with ID staff-row-${staffId} not found`);
                    }
                } else {
                    // Error alert with SweetAlert2
                    Swal.fire(
                        'Error!',
                        data.message || 'Failed to delete staff member.',
                        'error'
                    );
                }
            })
            .catch(error => {
                console.error('Error:', error);
                // Error alert with SweetAlert2
                Swal.fire(
                    'Error!',
                    'An error occurred while trying to delete the staff member.',
                    'error'
                );
            });
        }
    });
}

// Utility function to get the CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
