from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from . import models

# Create your views here.
#STAFF-SIDE

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

def staff_dashboard(request):
    # Check if staff is logged in
    if 'staff_id' not in request.session:
        return redirect('staff_login')
    
    # Get staff details
    staff_id = request.session['staff_id']
    staff = models.Staff.objects.get(staff_id=staff_id)
    
    return render(request, 'staffside/staffdashboard.html', {'staff': staff})

#ADMIN-SIDE
def admin_login(request):
    return render(request, 'auth/admin_login.html')
