# Generated by Django 5.1.4 on 2024-12-18 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_appointment_certificate_category_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='admin',
            name='contact_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='admin',
            name='full_name',
            field=models.CharField(default='Admin User', max_length=255),
        ),
        migrations.AddField(
            model_name='admin',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AddField(
            model_name='admin',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='admin_profile_images/'),
        ),
    ]
