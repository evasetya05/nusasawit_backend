from django.test import TestCase
from django.contrib.auth.models import User
from apps.core.models import Employee
from .models import Complaint

class ComplaintModelTest(TestCase):
    def setUp(self):
        # buat user + employee sample; sesuaikan field Employee Anda
        self.user = User.objects.create_user(username='tester', password='pass')
        # asumsi Employee memiliki field 'user' dan 'email'
        self.employee = Employee.objects.create(user=self.user, email='tester@example.com')
    
    def test_create_complaint(self):
        c = Complaint.objects.create(
            reporter=self.employee,
            title='Tes Keluhan',
            description='Deskripsi',
            status='submitted',
        )
        self.assertEqual(c.reporter, self.employee)
        self.assertEqual(str(c).startswith('['), True)
