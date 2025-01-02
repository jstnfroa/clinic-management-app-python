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
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count
import json

def patient_login(request):
    # Your login logic here
    patient = models.Patient.objects.get(email_address=request.POST['email_address'])
    
    # Set the session
    request.session['patient_id'] = patient.patient_id
    request.session['patient_email'] = patient.email_address
    
    # Optionally, set is_logged_in to True in the database if needed
    patient.is_logged_in = True
    patient.save()

    return redirect('patient_dashboard')

def patient_logout(request):
    # Your logout logic here
    patient = models.Patient.objects.get(patient_id=request.session['patient_id'])
    
    # Clear the session
    request.session.flush()
    
    # Optionally, set is_logged_in to False in the database if needed
    patient.is_logged_in = False
    patient.save()

    return redirect('patient_login')

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

    # Patients data
    patients = models.Patient.objects.all()
    total_patients = patients.count()

    # Count patients per college/office and get abbreviations
    college_patient_count = patients.values('college_office').annotate(patient_count=Count('college_office'))

    # Prepare the data for the chart with abbreviations
    college_offices = [item['college_office'] for item in college_patient_count]
    abbreviated_offices = [COLLEGE_ABBREVIATIONS.get(office, office) for office in college_offices]  # Use abbreviation or full name
    patient_counts = [item['patient_count'] for item in college_patient_count]

    age_ranges = {
        '0-17': 0,
        '18-25': 0,
        '26-40': 0,
        '41-60': 0,
        '60+': 0,
    }
    for patient in patients:
        if patient.age <= 17:
            age_ranges['0-17'] += 1
        elif 18 <= patient.age <= 25:
            age_ranges['18-25'] += 1
        elif 26 <= patient.age <= 40:
            age_ranges['26-40'] += 1
        elif 41 <= patient.age <= 60:
            age_ranges['41-60'] += 1
        else:
            age_ranges['60+'] += 1

    age_percentages = {k: (v / total_patients * 100) if total_patients else 0 for k, v in age_ranges.items()}

    # Active/Inactive Patients
    active_patients = patients.filter(is_logged_in=True).count()
    inactive_patients = total_patients - active_patients

    # Appointments data
    today = timezone.now().date()
    appointments_today = models.Appointment.objects.filter(date=today)
    total_appointments_today = appointments_today.count()
    scheduled_appointments = appointments_today.filter(status='Scheduled').count()
    completed_appointments = appointments_today.filter(status='Completed').count()
    canceled_appointments = appointments_today.filter(status='Canceled').count()

    start_of_week = today - timedelta(days=today.weekday())  # Start of the week (Monday)
    
    # Initialize a dictionary for consultations count per day
    daily_consultations = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}

    # Get consultations for the current week
    consultations = models.Appointment.objects.filter(
        date__range=[start_of_week, start_of_week + timedelta(days=4)]
    ).values('date').annotate(count=Count('appointment_id'))

    # Map the data to days of the week
    daily_consultations = {day: 0 for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
    for consultation in consultations:
        day_name = consultation['date'].strftime('%A')
        if day_name in daily_consultations:
            daily_consultations[day_name] = consultation['count']

    # Convert data into JSON for safe passing to JavaScript
    daily_consultations_json = json.dumps(list(daily_consultations.values()))

    # Staff data
    active_staff = models.Staff.objects.filter(status='Active')
    active_nurses = active_staff.filter(role='Nurse').count()
    active_dentists = active_staff.filter(role='Dentist').count()
    active_physicians = active_staff.filter(role='Physician').count()

    # Patient roles
    active_students = patients.filter(is_logged_in=True, patient_role='Student').count()
    active_faculty = patients.filter(is_logged_in=True, patient_role='Faculty').count()
    active_non_academic = patients.filter(is_logged_in=True, patient_role='Non-Academic Personnel').count()

    # Queue statuses
    queue_status_today = models.Appointment.objects.filter(date=today)
    patients_serving = queue_status_today.filter(queue_status='In Progress').count()
    patients_served = queue_status_today.filter(queue_status='Completed').count()
    patients_waiting = queue_status_today.filter(queue_status='Waiting').count()

    # Context
    context = {
        'staff': staff,
        'total_patients': total_patients,
        'active_patients': active_patients,
        'inactive_patients': inactive_patients,
        'total_appointments_today': total_appointments_today,
        'scheduled_appointments': scheduled_appointments,
        'completed_appointments': completed_appointments,
        'canceled_appointments': canceled_appointments,
        'active_nurses': active_nurses,
        'active_dentists': active_dentists,
        'active_physicians': active_physicians,
        'active_students': active_students,
        'active_faculty': active_faculty,
        'active_non_academic': active_non_academic,
        'patients_serving': patients_serving,
        'patients_served': patients_served,
        'patients_waiting': patients_waiting,
        'age_0_17': age_percentages['0-17'],
        'age_18_25': age_percentages['18-25'],
        'age_26_40': age_percentages['26-40'],
        'age_41_60': age_percentages['41-60'],
        'age_60_plus': age_percentages['60+'],
        'daily_consultations': daily_consultations_json,
        'college_offices': abbreviated_offices,
        'patient_counts': patient_counts,
    }

    return render(request, 'staffside/staffdashboard.html', context)


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

        try:
            admin = models.Admin.objects.get(email=email)
            if check_password(password, admin.password):  # Verifying the hashed password
                # Store session data
                request.session['admin_id'] = admin.admin_id
                request.session['admin_email'] = admin.email
                return JsonResponse({
                    'success': True,
                    'redirect_url': '/admin_dashboard/',  # Replace with actual dashboard URL
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error_message': 'Invalid email or password',
                })
        except models.Admin.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error_message': 'Admin does not exist',
            })
    
    # If GET request or form not submitted, return the login page
    return render(request, 'auth/admin_login.html')

# Define abbreviations for the colleges/departments
COLLEGE_ABBREVIATIONS = {
    'College of Architecture and Fine Arts (CAFA)': 'CAFA',
    'College of Arts and Letters (CAL)': 'CAL',
    'College of Business Education and Accountancy (CBEA)': 'CBEA',
    'College of Criminal Justice Education (CCJE)': 'CCJE',
    'College of Hospitality and Tourism Management (CHTM)': 'CHTM',
    'College of Information and Communications Technology (CICT)': 'CICT',
    'College of Industrial Technology (CIT)': 'CIT',
    'College of Law (CLaw)': 'CLaw',
    'College of Nursing (CN)': 'CN',
    'College of Engineering (COE)': 'COE',
    'College of Education (COED)': 'COED',
    'College of Science (CS)': 'CS', 
    'College of Sports, Exercise and Recreation (CSER)': 'CSER',
    'College of Social Sciences and Philosophy (CSSP)': 'CSSP',
    'Graduate School (GS)':'GS',
}

@admin_login_required
def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    admin_email = request.session['admin_email']
    admin = models.Admin.objects.get(email=admin_email)

    # Patients data
    patients = models.Patient.objects.all()
    total_patients = patients.count()

    # Count patients per college/office and get abbreviations
    college_patient_count = patients.values('college_office').annotate(patient_count=Count('college_office'))

    # Prepare the data for the chart with abbreviations
    college_offices = [item['college_office'] for item in college_patient_count]
    abbreviated_offices = [COLLEGE_ABBREVIATIONS.get(office, office) for office in college_offices]  # Use abbreviation or full name
    patient_counts = [item['patient_count'] for item in college_patient_count]

    age_ranges = {
        '0-17': 0,
        '18-25': 0,
        '26-40': 0,
        '41-60': 0,
        '60+': 0,
    }
    for patient in patients:
        if patient.age <= 17:
            age_ranges['0-17'] += 1
        elif 18 <= patient.age <= 25:
            age_ranges['18-25'] += 1
        elif 26 <= patient.age <= 40:
            age_ranges['26-40'] += 1
        elif 41 <= patient.age <= 60:
            age_ranges['41-60'] += 1
        else:
            age_ranges['60+'] += 1

    age_percentages = {k: (v / total_patients * 100) if total_patients else 0 for k, v in age_ranges.items()}

    # Active/Inactive Patients
    active_patients = patients.filter(is_logged_in=True).count()
    inactive_patients = total_patients - active_patients

    # Appointments data
    today = timezone.now().date()
    appointments_today = models.Appointment.objects.filter(date=today)
    total_appointments_today = appointments_today.count()
    scheduled_appointments = appointments_today.filter(status='Scheduled').count()
    completed_appointments = appointments_today.filter(status='Completed').count()
    canceled_appointments = appointments_today.filter(status='Canceled').count()

    start_of_week = today - timedelta(days=today.weekday())  # Start of the week (Monday)
    
    # Initialize a dictionary for consultations count per day
    daily_consultations = {day: 0 for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']}

    # Get consultations for the current week
    consultations = models.Appointment.objects.filter(
        date__range=[start_of_week, start_of_week + timedelta(days=4)]
    ).values('date').annotate(count=Count('appointment_id'))

    # Map the data to days of the week
    daily_consultations = {day: 0 for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]}
    for consultation in consultations:
        day_name = consultation['date'].strftime('%A')
        if day_name in daily_consultations:
            daily_consultations[day_name] = consultation['count']

    # Convert data into JSON for safe passing to JavaScript
    daily_consultations_json = json.dumps(list(daily_consultations.values()))

    # Staff data
    active_staff = models.Staff.objects.filter(status='Active')
    active_nurses = active_staff.filter(role='Nurse').count()
    active_dentists = active_staff.filter(role='Dentist').count()
    active_physicians = active_staff.filter(role='Physician').count()

    # Patient roles
    active_students = patients.filter(is_logged_in=True, patient_role='Student').count()
    active_faculty = patients.filter(is_logged_in=True, patient_role='Faculty').count()
    active_non_academic = patients.filter(is_logged_in=True, patient_role='Non-Academic Personnel').count()

    # Queue statuses
    queue_status_today = models.Appointment.objects.filter(date=today)
    patients_serving = queue_status_today.filter(queue_status='In Progress').count()
    patients_served = queue_status_today.filter(queue_status='Completed').count()
    patients_waiting = queue_status_today.filter(queue_status='Waiting').count()

    # Context
    context = {
        'admin': admin,
        'total_patients': total_patients,
        'active_patients': active_patients,
        'inactive_patients': inactive_patients,
        'total_appointments_today': total_appointments_today,
        'scheduled_appointments': scheduled_appointments,
        'completed_appointments': completed_appointments,
        'canceled_appointments': canceled_appointments,
        'active_nurses': active_nurses,
        'active_dentists': active_dentists,
        'active_physicians': active_physicians,
        'active_students': active_students,
        'active_faculty': active_faculty,
        'active_non_academic': active_non_academic,
        'patients_serving': patients_serving,
        'patients_served': patients_served,
        'patients_waiting': patients_waiting,
        'age_0_17': age_percentages['0-17'],
        'age_18_25': age_percentages['18-25'],
        'age_26_40': age_percentages['26-40'],
        'age_41_60': age_percentages['41-60'],
        'age_60_plus': age_percentages['60+'],
        'daily_consultations': daily_consultations_json,
        'college_offices': abbreviated_offices,
        'patient_counts': patient_counts,
    }

    return render(request, 'superadminside/admindashboard.html', context)

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
        'status': staff.status,
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
        staff.status = request.POST.get('status')
        
        # Optionally handle profile image and password updates
        if 'profile_image' in request.FILES:
            staff.profile_image = request.FILES['profile_image']
        
        staff.save()  # Save the updated staff details

        return JsonResponse({'success': True, 'message': 'Staff updated successfully'})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})

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

