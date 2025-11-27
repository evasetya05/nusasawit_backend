from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from faker import Faker
import random
from apps.core.models import Company, Employee, Department, Position
from django.contrib.auth.models import Group, Permission

User = get_user_model()
fake = Faker('id_ID')  # Using Indonesian locale for more realistic local data

class Command(BaseCommand):
    help = 'Creates test data including companies, owners, managers, and employees'

    def add_arguments(self, parser):
        parser.add_argument(
            '--companies',
            type=int,
            default=2,
            help='Number of companies to create (default: 2)'
        )
        parser.add_argument(
            '--managers-per-company',
            type=int,
            default=2,
            help='Number of managers per company (default: 2)'
        )
        parser.add_argument(
            '--employees-per-company',
            type=int,
            default=10,
            help='Number of employees per company (default: 10)'
        )
        parser.add_argument(
            '--login-ratio',
            type=float,
            default=0.5,
            help='Ratio of employees who can login (default: 0.5)'
        )

    def create_company(self):
        """Helper method to create a company with its employees"""
        # Create company
        company_name = f"{fake.company()} {' '.join(fake.words(1)).title()}"
        company = Company.objects.create(
            name=company_name,
            address=fake.street_address(),
            phone=''.join(c for c in fake.phone_number() if c.isdigit())[:15],
            email=fake.company_email(),
            website=fake.url(),
            plan=random.choice(['free', 'pro', 'enterprise']),
            plan_expires_at=timezone.now() + timedelta(days=random.randint(30, 730))
        )
        self.stdout.write(self.style.SUCCESS(f'Created company: {company.name}'))
        return company

    def create_employee(self, company, department, position, manager=None, can_login=False):
        """Helper method to create an employee"""
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 100)}@{fake.domain_name()}"

        user = None
        if can_login:
            username = f"{first_name.lower()}{random.randint(1, 100)}"
            user = User.objects.create_user(
                username=username,
                email=email,
                company=company,
                password='password123',
                is_active=True
            )

        employee = Employee.objects.create(
            name=f"{first_name} {last_name}",
            email=email,
            user=user,
            company=company,
            department=department,
            position=position,
            manager=manager,
            hire_date=fake.date_between(start_date='-5y', end_date='today'),
            is_active=random.choices([True, False], weights=[0.9, 0.1])[0],
            basic_salary=random.randint(5000000, 30000000) // 100000 * 100000,  # Rounded to nearest 100k
            default_allowance=random.randint(500000, 3000000) // 100000 * 100000,
            phone=''.join(c for c in fake.phone_number() if c.isdigit())[:15],
            address=fake.address()
        )

        if user:
            login_info = f" (login: {user.username})"
        else:
            login_info = " (no login)"

        position_info = position.name.lower() if position else 'employee'
        self.stdout.write(self.style.SUCCESS(
            f'Created {position_info}: {employee.name}{login_info} at {company.name}'))

        return employee

    @transaction.atomic
    def handle(self, *args, **options):
        num_companies = options['companies']
        managers_per_company = options['managers_per_company']
        employees_per_company = options['employees_per_company']
        login_ratio = options['login_ratio']

        self.stdout.write(self.style.MIGRATE_HEADING('Starting to create test data...'))
        self.stdout.write(f"Companies: {num_companies}")
        self.stdout.write(f"Managers per company: {managers_per_company}")
        self.stdout.write(f"Employees per company around: {employees_per_company}")
        self.stdout.write(f"Login ratio: {login_ratio*100}% of employees will have login access")

        # Create companies
        companies = []
        for i in range(num_companies):
            company = self.create_company()
            companies.append(company)

            # Create departments
            departments = []
            for dept_name in ['Engineering', 'Marketing', 'HR', 'Finance', 'Operations']:
                dept = Department.objects.create(
                    name=dept_name,
                    company=company
                )
                departments.append(dept)

            # Create positions
            positions = []
            for _ in range(3):
                title = fake.job()
                if random.random() < 0.5:  # 50% chance to be a manager
                    title = f"{title} Manager"
                pos = Position.objects.create(
                    name=title,
                    department=random.choice(departments)
                )
                positions.append(pos)
            for _ in range(2):
                pos = Position.objects.create(
                    name=fake.job(),
                    department=random.choice(departments)
                )
                positions.append(pos)

            # Create company owner (with login access)
            owner = self.create_employee(
                company=company,
                department=random.choice(departments),
                position=random.choice([p for p in positions if 'Manager' in p.name] or [None]),
                can_login=True,
            )
            owner.user.groups.add(Group.objects.get(name='Owner'))
            company.owner = owner.user
            company.save()

            # Create managers
            managers = [owner]
            for _ in range(managers_per_company - 1):  # -1 because owner is already a manager
                manager = self.create_employee(
                    company=company,
                    department=random.choice(departments),
                    position=random.choice([p for p in positions if 'Manager' in p.name] or [None]),
                    can_login=random.random() < 0.8,  # 80% of managers can login
                )
                if manager.user:  # If manager has login access
                    managers.append(manager)

            # Create regular employees with random count around the specified number (±20%)
            employee_count = max(1, int(employees_per_company * random.uniform(0.8, 1.2)))
            for _ in range(employee_count):
                self.create_employee(
                    company=company,
                    department=random.choice(departments),
                    position=random.choice([p for p in positions if 'Manager' not in p.name]),
                    manager=random.choice(managers) if managers and random.random() < 0.8 else None,
                    can_login=random.random() < login_ratio
                )

        # Print login information for users with accounts
        users_with_login = User.objects.filter(is_active=True)
        if users_with_login.exists():
            self.stdout.write(self.style.SUCCESS('\nLogin Information:'))
            self.stdout.write('=' * 35)
            self.stdout.write('{:<15} {:<20}'.format('Username', 'Role'))
            self.stdout.write('-' * 35)
            for user in users_with_login:
                role = 'Admin' if user.is_staff else 'Regular User'
                if hasattr(user, 'person') and user.person.manager is None:
                    role = 'Company Owner'
                self.stdout.write('{:<15} {:<20}'.format(
                    user.username,
                    role
                ))

        self.stdout.write(self.style.SUCCESS('\nSuccessfully created test data!'))
        self.stdout.write(f'\nAdmin URL: http://localhost:8000/admin/')
        self.stdout.write(f'Login URL: http://localhost:8000/accounts/login/')
