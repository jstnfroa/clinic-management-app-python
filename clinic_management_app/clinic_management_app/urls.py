"""
URL configuration for clinic_management_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import main.views as views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('staff_login/', views.staff_login, name='staff_login'),
    path('admin_login/', views.admin_login, name='admin_login'),
    
    #PATIENT-SIDE

    # STAFF-SIDE
    path('staff_dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff_queuing/', views.staff_queuing, name='staff_queuing'),
    path('staff_add_patient/', views.staff_add_patient, name='staff_add_patient'),
    path('staff_patient_record/', views.staff_patient_record, name='staff_patient_record'),
    path('staff_profile/', views.staff_profile, name='staff_profile'),
    path('logout_staff/', views.staff_logout, name='logout_staff'),

    # ADMIN-SIDE
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user_management/', views.admin_user_management, name='user_management'),
    path('admin_profile/', views.admin_profile, name='admin_profile'),
    path('logout_admin/', views.admin_logout, name='logout_admin'),
    path('update-profile-image/', views.update_profile_image, name='update_profile_image'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
