from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from functools import wraps
from django.contrib import messages
from . import models

# Create your views here.
def staff_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'staff_id' not in request.session:
            return redirect('staff_login')  # Redirect to your staff login page
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'admin_id' not in request.session:
            return redirect('admin_login')  # Redirect to the admin login page
        return view_func(request, *args, **kwargs)
    return _wrapped_view

#PATIENT-SIDE

#STAFF-SIDE
def staff_logout(request):
    logout(request)  # Clear session data
    return redirect('staff_login')  # Redirect to login page

def admin_logout(request):
    logout(request)  # Clear session data
    return redirect('admin_login')  # Redirect to login page

def staff_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate staff
        try:
            staff = models.Staff.objects.get(email_address=email)
            if check_password(password, staff.password):  # Verifying the hashed password
                # Store session data
                request.session['staff_id'] = staff.staff_id
                request.session['staff_name'] = staff.name
                return JsonResponse({
                    'success': True,
                    'redirect_url': '/staff_dashboard/',  # Replace with actual dashboard URL
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error_message': 'Invalid email or password',
                })
        except models.Staff.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error_message': 'Staff does not exist',
            })
    
    # If GET request or form not submitted, return the login page
    return render(request, 'auth/staff_login.html')

@staff_login_required
def staff_dashboard(request):
    # Check if staff is logged in
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    # Get staff details
    staff_id = request.session['staff_id']
    staff = models.Staff.objects.get(staff_id=staff_id)
    
    return render(request, 'staffside/staffdashboard.html', {'staff': staff})

@staff_login_required
def staff_queuing(request):
    # Check if staff is logged in
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    # Get staff details
    staff_id = request.session['staff_id']
    staff = models.Staff.objects.get(staff_id=staff_id)
    
    return render(request, 'staffside/staffqueuing.html', {'staff': staff})

@staff_login_required
def staff_add_patient(request):
    # Check if staff is logged in
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    # Get staff details
    staff_id = request.session['staff_id']
    staff = models.Staff.objects.get(staff_id=staff_id)
    
    return render(request, 'staffside/addpatient.html', {'staff': staff})

@staff_login_required
def staff_patient_record(request):
    # Check if staff is logged in
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    # Get staff details
    staff_id = request.session['staff_id']
    staff = models.Staff.objects.get(staff_id=staff_id)
    
    return render(request, 'staffside/patientrecord.html', {'staff': staff})

@staff_login_required
def staff_profile(request):
    # Check if staff is logged in
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    # Get staff details
    staff_id = request.session['staff_id']
    staff = models.Staff.objects.get(staff_id=staff_id)
    
    return render(request, 'staffside/profile.html', {'staff': staff})

#ADMIN-SIDE
def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate admin
        try:
            admin = models.Admin.objects.get(email=email)
            if check_password(password, admin.password):  # Verifying the hashed password
                # Store session data for admin
                request.session['admin_id'] = admin.admin_id
                request.session['admin_email'] = admin.email  # Storing email as 'admin_name'
                return redirect('admin_dashboard')  # Redirect to admin dashboard after successful login
            else:
                messages.error(request, 'Invalid email or password')  # Error message
        except models.Admin.DoesNotExist:
            messages.error(request, 'Admin does not exist')  # Error message

    return render(request, 'auth/admin_login.html')

@admin_login_required
def admin_dashboard(request):
    # Ensure the admin is logged in
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    # Retrieve admin details from session
    admin_email = request.session['admin_email']
    admin = models.Admin.objects.get(email=admin_email)

    return render(request, 'superadminside/admindashboard.html', {'admin': admin})

@admin_login_required
def admin_user_management(request):
    # Ensure the admin is logged in
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    # Retrieve admin details from session
    admin_email = request.session['admin_email']
    admin = models.Admin.objects.get(email=admin_email)

    return render(request, 'superadminside/user_management.html', {'admin': admin})

@admin_login_required
def admin_profile(request):
    # Ensure the admin is logged in
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    # Retrieve admin details from session
    admin_email = request.session['admin_email']
    admin = models.Admin.objects.get(email=admin_email)

    # Handle profile update form submission
    if request.method == 'POST':
        # Get updated data from form
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact_number')
        
        # Ensure the email is not empty
        if not email:
            messages.error(request, "Email is required")
            return redirect('admin_profile')

        # Update admin details (excluding password)
        admin.full_name = full_name
        admin.email = email
        admin.contact_number = contact_number

        # Handle profile image update (if uploaded)
        if request.FILES.get('profile_image'):
            admin.profile_image = request.FILES['profile_image']

        # Save the updated admin details (without changing the password)
        admin.save()

        # Show success message
        messages.success(request, "Profile updated successfully!")
        return redirect('admin_profile')  # Redirect to the same page to reflect changes

    # Pass the admin details to the template
    return render(request, 'superadminside/profile.html', {'admin': admin, 'role': admin.role})