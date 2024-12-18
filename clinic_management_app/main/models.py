from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractUser
from django.db import models
#Patient Model
class Patient(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    PRIORITY_TYPE_CHOICES = [
        ('PWD', 'PWD'),
        ('Senior', 'Senior'),
        ('Personnel', 'Personnel'),
        ('Regular', 'Regular'),
    ]

    PATIENT_ROLE_CHOICES= [
        ('Student', 'Student'),
        ('Faculty','Faculty'),
        ('Non-Academic Personnel', 'Non-Academic Personnel'),
    ]

    COLLEGE_OFFICE_CHOICES= [
        ('College of Architecture and Fine Arts (CAFA)', 'College of Architecture and Fine Arts (CAFA)'),
        ('College of Arts and Letters (CAL)', 'College of Arts and Letters (CAL)'),
        ('College of Business Education and Accountancy (CBEA)', 'College of Business Education and Accountancy (CBEA)'),
        ('College of Criminal Justice Education (CCJE)', 'College of Criminal Justice Education (CCJE)'),
        ('College of Hospitality and Tourism Management (CHTM)', 'College of Hospitality and Tourism Management (CHTM)'),
        ('College of Information and Communications Technology (CICT)','College of Information and Communications Technology (CICT)'),
        ('College of Industrial Technology (CIT)', 'College of Industrial Technology (CIT)'),
        ('College of Law (CLaw)', 'College of Law (CLaw)'),
        ('College of Nursing (CN)', 'College of Nursing (CN)'),
        ('College of Engineering (COE)', 'College of Engineering (COE)'),
        ('College of Education (COED)', 'College of Education (COED)'),
        ('College of Science (CS)', 'College of Science (CS)'),
        ('College of Sports, Exercise and Recreation (CSER)', 'College of Sports, Exercise and Recreation (CSER)'),
        ('College of Social Sciences and Philosophy (CSSP)', 'College of Social Sciences and Philosophy (CSSP)'),
        ('Graduate School (GS)','Graduate School (GS)'),
    ]

    patient_id = models.AutoField(primary_key=True, verbose_name="Patient ID")
    student_employee_id= models.IntegerField(unique=True,null=True,verbose_name="Student Employee ID")
    first_name = models.CharField(max_length=50, verbose_name="First Name")
    middle_name = models.CharField(max_length=50, verbose_name="Middle Name", blank=True, null=True)
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    @property
    def full_name(self):
        return f"{self.middle_name} {self.last_name}"
    age = models.IntegerField()
    sex = models.CharField(max_length=6, choices=[('Male', 'Male'), ('Female', 'Female')])
    email_address = models.EmailField(unique=True, verbose_name="Email Address")
    password = models.CharField(max_length=255)
    # Replace with hashed password handling
    contact_number = models.CharField(max_length=15, verbose_name="Contact Number")
    medical_history = models.TextField(blank=True, null=True)
    address_lot_no = models.CharField(max_length=50, null=True, verbose_name="Address Lot Number")
    address_street = models.CharField(max_length=50, null=True, verbose_name="Address Street Number")
    address_barangay = models.CharField(max_length=50, null= True, verbose_name="Address Barangay")
    address_municipality = models.CharField(max_length=50, null=True, verbose_name="Address Municipality")
    address_province = models.CharField(max_length=50, null=True, verbose_name="Address Province")
    campus = models.CharField(max_length=100, verbose_name="Campus")
    college_office = models.CharField(max_length=100, null=True, choices= COLLEGE_OFFICE_CHOICES,verbose_name="College/Office")
    course_year_section = models.CharField(max_length=100, verbose_name="Course/Year/Section")
    emergency_contact = models.CharField(max_length=100, verbose_name="Emergency Contact Name")
    emergency_contact_number = models.CharField(max_length=15, verbose_name="Emergency Contact Number")
    blood_type = models.CharField(max_length=3, null=True, choices=BLOOD_TYPE_CHOICES)
    patient_role = models.CharField(max_length=25, null=True, choices=PATIENT_ROLE_CHOICES)
    priority_type= models.CharField(max_length=10, null=True, choices=PRIORITY_TYPE_CHOICES)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)

    @property
    def full_address(self):
        return f"{self.address_lot_no } {self.address_street} {self.address_barangay} , {self.address_municipality}, {self.address_province}"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.patient_id})"


#Staff Model
class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True)
    admin = models.ForeignKey('Admin', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=50,
        choices=[
            ('Nurse', 'Nurse'),
            ('Dentist', 'Dentist'),
            ('Physician', 'Physician')
        ]
    )
    email_address = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)

    def save(self, *args, **kwargs):
        if self.password:  # Hash the password only if it's not already hashed
            self.password = make_password(self.password)
        super(Staff, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


#Admin Model
class Admin(models.Model):
    admin_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    profile_image = models.ImageField(upload_to='admin_profile_pics/', blank=True, null=True)
    role = models.CharField(max_length=50, default='Super Admin')

    def save(self, *args, **kwargs):
        if self.password:  # Hash the password only if it's not already hashed
            self.password = make_password(self.password)
        super(Admin, self).save(*args, **kwargs)

    def __str__(self):
        return self.email


#Appointment Model
class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True, verbose_name="Appointment ID") #Auto created
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE) #patient as reference
    date = models.DateField() #Current date will be saved
    time = models.TimeField() #Current time will be saved
    status = models.CharField(
        max_length=20,
        choices=[
            ('Scheduled', 'Scheduled'),
            ('Canceled', 'Canceled'),
            ('Completed', 'Completed')
        ]
    ) #Save 'Scheduled' for now everytime the appointment is created.

    transaction_type = models.CharField(
        max_length=50,
        choices=[
            ('Consultation', 'Consultation'),
            ('Certificates', 'Certificates'),
            ('Others', 'Others')
        ]
    )#Save depends on what container to be picked in patient_queue view.

    ticket_type = models.CharField(
        max_length=50, null=True,
        choices=[
            ('Appointment', 'Appointment'),
            ('Walk-in', 'Walkin')
        ]
    )#Save depends on what container to be picked in patient_queue view. 
    queue_type = models.CharField(
        max_length=20,
        choices=[
            ('Priority', 'Priority'),
            ('Regular', 'Regular')
        ] #Save as 'Priority' if the current Patient priority_type is either 'PWD', 'Senior', or 'Personnel'.
    )
    queue_status = models.CharField(
        max_length=20,
        choices=[
            ('Waiting', 'Waiting'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed')
        ]
    ) #Save as 'In Progress' for now when the Appointment is created.

    certificate_category = models.CharField(
        max_length=40, null=True,
        choices = [
            ('Absence Certificate', 'Absence Certificate'),
            ('Employment Certificate', 'Employment Certificate'),
            ('OJT Certificate', 'OJT Certificate'),
            ('OSRA Certificate', 'OSRA Certificate'),
        ] #Save depends on what container to be picked in patient_queue view.
    )

    queue_category = models.CharField(
        max_length=20, null=True,
        choices=[
            ('Medical', 'Medical'),
            ('Dental', 'Dental'),
        ]
    )  #Save depends on what container to be picked in patient_queue view.
    def __str__(self):
        return f"Appointment {self.appointment_id} - {self.patient}"


# Medical Record Model
class MedicalRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    date_of_diagnosis = models.DateField()
    initial_diagnosis = models.TextField()
    attending_staff = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=50)
    assessment = models.TextField()
    prescription = models.TextField()

    def __str__(self):
        return f"Record {self.record_id} - {self.patient}"