from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, render
from django.core.files.storage import FileSystemStorage
from functools import wraps
from django.contrib import messages
from . import models
from .models import Staff

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

    # Get the search query from the request (if any)
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role_filter', '')
    filter_option = request.GET.get('filter', '')

    # Get staff list, filtered by search query if present
    staff_list = models.Staff.objects.all()

    if search_query:
        staff_list = staff_list.filter(name__icontains=search_query)

    # Apply the role filter if provided
    if role_filter:
        staff_list = staff_list.filter(role=role_filter)

    # Apply the filter option (alphabetical, newest)
    if filter_option == 'alphabetical':
        staff_list = staff_list.order_by('name')  # Alphabetical order
    elif filter_option == 'newest':
        staff_list = staff_list.order_by('-staff_id')  # Newest first (based on staff_id)

    # Handle staff creation (existing code)
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Process the form data to add new staff
        fullname = request.POST.get('fullname')
        role = request.POST.get('role')
        email_address = request.POST.get('email-address')
        contact_number = request.POST.get('contact-number')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        profile_image = request.FILES.get('profile-image')

        # Check if password and confirm password match
        if password != confirm_password:
            return JsonResponse({'error': 'Passwords do not match'}, status=400)

        # Hash the password before saving
        hashed_password = make_password(password)

        # Save the profile image if uploaded
        fs = FileSystemStorage()
        if profile_image:
            profile_image_path = fs.save(profile_image.name, profile_image)
            profile_image_url = fs.url(profile_image_path)
        else:
            profile_image_url = None

        # Create the staff member
        try:
            new_staff = models.Staff.objects.create(
                admin=admin,
                name=fullname,
                role=role,
                email_address=email_address,
                password=hashed_password,
                contact_number=contact_number,
                profile_image=profile_image_url
            )
            return JsonResponse({'message': 'Staff added successfully'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    # Render the template with staff list, admin details, search query, and filter options
    return render(request, 'superadminside/user_management.html', {
        'admin': admin, 
        'staff_list': staff_list, 
        'search_query': search_query, 
        'role_filter': role_filter
    })

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
        # If the form has password change data
        if 'old_password' in request.POST:
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            # Validate the old password (make sure it's correct)
            if not check_password(old_password, admin.password):
                messages.error(request, "Old password is incorrect.")
                return redirect('admin_profile')  # Redirect to admin profile page

            # Ensure new password and confirm password match
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return redirect('admin_profile')

            # Update password in the database
            admin.password = make_password(new_password)
            admin.save()

            # Show success message
            messages.success(request, "Password changed successfully!")
            return redirect('admin_profile')  # Redirect to profile page after password change

        # Handle other profile data (if it's not a password change)
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact_number')

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

        messages.success(request, "Profile updated successfully!")
        return redirect('admin_profile')  # Redirect to the same page to reflect changes

    return render(request, 'superadminside/profile.html', {'admin': admin, 'role': admin.role})

@admin_login_required
def update_profile_image(request):
    if request.method == 'POST' and request.FILES.get('profile_image'):
        try:
            # Retrieve admin email from session (same as in admin_profile view)
            admin_email = request.session.get('admin_email')
            if not admin_email:
                return JsonResponse({'success': False, 'error': 'Admin email not found in session.'}, status=400)

            # Retrieve the Admin object based on the session email
            admin = models.Admin.objects.get(email=admin_email)
            
            # Update the profile image
            admin.profile_image = request.FILES['profile_image']
            admin.save()

            return JsonResponse({'success': True})

        except ObjectDoesNotExist:
            # Handle case when Admin object is not found
            return JsonResponse({'success': False, 'error': 'Admin user does not exist.'}, status=404)

    return JsonResponse({'success': False, 'error': 'No profile image provided.'}, status=400)

# View staff details
def view_staff(request, staff_id):
    staff = get_object_or_404(Staff, pk=staff_id)
    staff_data = {
        'staff_id': staff.staff_id,
        'name': staff.name,
        'role': staff.role,
        'email_address': staff.email_address,
        'contact_number': staff.contact_number,
        'profile_image': staff.profile_image.url if staff.profile_image else None
    }
    return JsonResponse({'staff': staff_data})

# Edit staff details
def edit_staff(request, staff_id):
    staff = get_object_or_404(Staff, pk=staff_id)
    
    if request.method == 'POST':
        staff.name = request.POST.get('name')
        staff.role = request.POST.get('role')
        staff.email_address = request.POST.get('email_address')
        staff.contact_number = request.POST.get('contact_number')

        # Optionally handle profile image and password updates
        if 'profile_image' in request.FILES:
            staff.profile_image = request.FILES['profile_image']
        
        staff.save()  # Save the updated staff details

        # Return a JSON response indicating success
        return JsonResponse({'success': True, 'message': 'Staff updated successfully'})

    return render(request, 'superadminside/edit_staff.html', {'staff': staff})

# Delete staff member
def delete_staff(request, staff_id):
    if request.method == 'POST':
        try:
            staff = get_object_or_404(Staff, staff_id=staff_id)
            staff.delete()
            return JsonResponse({'status': 'success'}, status=200)
        except Staff.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Staff not found'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

