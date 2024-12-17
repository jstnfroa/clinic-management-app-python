from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from functools import wraps
from . import models

# Create your views here.
def staff_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'staff_id' not in request.session:
            return redirect('staff_login')  # Redirect to your staff login page
        return view_func(request, *args, **kwargs)
    return _wrapped_view

#STAFF-SIDE
def staff_logout(request):
    logout(request)  # Clear session data
    return redirect('staff_login')  # Redirect to login page

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
    return render(request, 'auth/admin_login.html')
