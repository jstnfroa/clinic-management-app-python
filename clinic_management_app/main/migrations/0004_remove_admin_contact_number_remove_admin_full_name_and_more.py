# Generated by Django 5.1.4 on 2024-12-18 17:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_admin_contact_number_admin_full_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='admin',
            name='contact_number',
        ),
        migrations.RemoveField(
            model_name='admin',
            name='full_name',
        ),
        migrations.RemoveField(
            model_name='admin',
            name='last_login',
        ),
        migrations.RemoveField(
            model_name='admin',
            name='profile_image',
        ),
    ]