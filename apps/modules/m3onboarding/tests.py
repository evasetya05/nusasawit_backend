from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.models import Company, Department, Position, Employee
from apps.modules.m3onboarding.views import EmployeeListView
from apps.modules.m3onboarding.forms import EmployeeForm

User = get_user_model()


class EmployeeListViewTest(TestCase):
    def setUp(self):
        # Create test data
        self.company = Company.objects.create(name='Test Company')
        self.department = Department.objects.create(name='HR', company=self.company)
        self.position = Position.objects.create(name='Manager', department=self.department)

        # Create users
        self.owner = User.objects.create_user(
            username='owner',
            email='owner@test.com',
            password='testpass123',
            company=self.company
        )
        self.company.owner = self.owner
        self.company.save()

        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@test.com',
            password='testpass123',
            company=self.company
        )

        # Create test employees
        self.employee1 = Employee.objects.create(
            name='John Doe',
            email='john@test.com',
            company=self.company,
            department=self.department,
            position=self.position
        )
        self.employee2 = Employee.objects.create(
            name='Jane Smith',
            email='jane@test.com',
            company=self.company,
            department=self.department,
            position=self.position
        )

        # Set up request factory
        self.factory = RequestFactory()
        self.url = reverse('m3onboarding:struktur_organisasi')

    def test_owner_sees_employee_list(self):
        """Test that owner can see the employee list"""
        self.client.force_login(self.owner)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('m3onboarding/struktur_organisasi/employee_list.html')
        self.assertIn('employees', response.context)
        self.assertIn(self.employee1, response.context['employees'])
        self.assertIn(self.employee2, response.context['employees'])

    def test_employee_sees_employee_index(self):
        """Test that regular employee sees the employee index"""
        self.client.force_login(self.employee_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('m3onboarding/struktur_organisasi/index.html')

    def test_owner_can_create_employee(self):
        """Test that owner can create a new employee"""
        self.client.force_login(self.owner)

        data = {
            'name': 'New Employee',
            'email': 'new@test.com',
            'department': self.department.id,
            'position': self.position.id,
            'phone': '1234567890',
            'address': '123 Test St',
            'hire_date': '2023-01-01'
        }

        response = self.client.post(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Employee.objects.filter(email='new@test.com').exists())

    def test_non_owner_cannot_create_employee(self):
        """Test that non-owner cannot create a new employee"""
        self.client.force_login(self.employee_user)

        data = {
            'name': 'New Employee',
            'email': 'new@test.com',
            'department': self.department.id,
            'position': self.position.id,
            'phone': '1234567890',
            'address': '123 Test St',
            'hire_date': '2023-01-01'
        }

        response = self.client.post(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Employee.objects.filter(email='new@test.com').exists())

    def test_employee_creation_requires_authentication(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_employee_list_filters_by_company(self):
        """Test that employees are filtered by the user's company"""
        # Create another company and employee
        other_company = Company.objects.create(name='Other Company')
        other_company.owner = User.objects.create_user(
            username='other_owner',
            email='other@test.com',
            password='testpass123',
            company=other_company
        )
        other_company.save()

        other_employee = Employee.objects.create(
            name='Other Employee',
            email='other@test.com',
            company=other_company,
            department=self.department,
            position=self.position
        )

        # Login as the first company's owner
        self.client.force_login(self.owner)
        response = self.client.get(self.url)

        # Should only see employees from the owner's company
        self.assertEqual(len(response.context['employees']), 2)  # The two employees created in setUp
        self.assertNotIn(other_employee, response.context['employees'])

    def test_employee_creation_invalid_form(self):
        """Test employee creation with invalid form data"""
        self.client.force_login(self.owner)

        # Missing required fields
        data = {
            'name': '',  # Required field
            'email': 'invalid-email',  # Invalid email
        }

        response = self.client.post(self.url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Employee.objects.filter(email='invalid-email').exists())
        self.assertIn('errors', response.json())
