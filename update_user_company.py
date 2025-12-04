#!/usr/bin/env python
import os
import sys
import django

# Add the project path to sys.path
sys.path.append('/home/eva/app/python/django/3.nusasawit_backend/nusasawit_backend')

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nusasawit_backend.settings')

# Setup Django
django.setup()

from apps.account.models import SystemUser
from apps.core.models import Company

def update_pengecek2_company():
    try:
        # Find user pengecek2
        user = SystemUser.objects.get(username='pengecek2')
        print(f"Found user: {user.username}")
        print(f"Current company: {user.company}")
        
        # Find company tes_sdmportabel
        company = Company.objects.get(name='tes_sdmportabel')
        print(f"Found company: {company.name}")
        
        # Update user's company
        user.company = company
        user.save()
        
        print(f"Successfully updated {user.username}'s company to {company.name}")
        
        # Verify the update
        updated_user = SystemUser.objects.get(username='pengecek2')
        print(f"Verification - Updated company: {updated_user.company}")
        
    except SystemUser.DoesNotExist:
        print("Error: User 'pengecek2' not found")
    except Company.DoesNotExist:
        print("Error: Company 'tes_sdmportabel' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    update_pengecek2_company()
