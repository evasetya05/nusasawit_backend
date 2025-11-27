from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from faker import Faker
import random
from apps.core.models import Company
from apps.modules.kinerja4.models import KPICycle

fake = Faker("id_ID")  # Using Indonesian locale for more realistic local data


class Command(BaseCommand):
    help = "Creates test KPI cycles for a selected company"

    def add_arguments(self, parser):
        parser.add_argument(
            "--company-id",
            type=int,
            help="ID of the company to create KPI cycles for (if not provided, will show a list to choose from)",
        )
        parser.add_argument(
            "--cycles",
            type=int,
            default=5,
            help="Number of KPI cycles to create (default: 3)",
        )

    def display_companies(self):
        """Display a list of available companies and return the selected company"""
        companies = list(Company.objects.all().order_by('id'))

        if not companies:
            self.stderr.write(self.style.ERROR("No companies found. Please create companies first."))
            return None

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(" Available Companies ".center(50, "=")))
        self.stdout.write("=" * 50)

        for i, company in enumerate(companies, 1):
            self.stdout.write(f"{i:>3}. {company.name:<40} (ID: {company.id})")

        self.stdout.write("-" * 50)
        self.stdout.write("  0. Cancel")
        self.stdout.write("=" * 50 + "\n")

        while True:
            try:
                choice = input("Select a company (number) or 0 to cancel: ").strip()
                if not choice:
                    continue

                choice_num = int(choice)
                if choice_num == 0:
                    self.stdout.write(self.style.WARNING("Operation cancelled by user."))
                    return None

                if 1 <= choice_num <= len(companies):
                    return companies[choice_num - 1]

                self.stderr.write(f"Please enter a number between 1 and {len(companies)} or 0 to cancel.")

            except ValueError:
                self.stderr.write("Invalid input. Please enter a number.")

    def handle(self, *args, **options):
        num_cycles = options["cycles"]

        # If company_id is provided, use it; otherwise, show interactive selection
        if options["company_id"] is not None:
            try:
                company = Company.objects.get(pk=options["company_id"])
            except Company.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Company with ID {options['company_id']} does not exist"))
                return
        else:
            company = self.display_companies()
            if not company:
                return  # User cancelled or no companies available

        self.create_kpi_cycles(company, num_cycles)

    def create_kpi_cycles(self, company, num_cycles):
        """Create test KPI cycles for the given company with random data"""
        periods = [choice[0] for choice in KPICycle.Period.choices]
        period_names = dict(KPICycle.Period.choices)

        today = timezone.now().date()
        created_count = 0

        with transaction.atomic():
            for _ in range(num_cycles):
                # Random period type
                period = random.choice(periods)

                # Random start date within ±2 years from today
                days_offset = random.randint(-730, 730)  # ±2 years
                start_date = today + timedelta(days=days_offset)

                # Random duration based on period
                if period == KPICycle.Period.WEEKLY:
                    duration_days = random.choice([30, 60, 90])  # 1-3 months
                elif period == KPICycle.Period.MONTHLY:
                    duration_days = random.choice([90, 180, 365])  # 3-12 months
                elif period == KPICycle.Period.QUARTERLY:
                    duration_days = random.choice([180, 365])  # 6-12 months
                elif period == KPICycle.Period.SEMIANNUAL:
                    duration_days = random.choice([365, 730])  # 1-2 years
                else:  # ANNUAL
                    duration_days = random.choice([365, 730, 1095])  # 1-3 years

                end_date = start_date + timedelta(days=duration_days)

                # Random active status (20% chance of being active)
                is_active = random.random() < 0.5

                # Generate random name using faker
                random_words = ' '.join(fake.words(3)).title()
                period_name = period_names[period]
                name = f"{random_words} - {period_name} {fake.date_between(start_date='-1y', end_date='+1y').strftime('%Y')}"

                # Create KPI cycle
                kpi_cycle = KPICycle.objects.create(
                    company=company,
                    name=name,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    active=is_active,
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created KPI Cycle: {kpi_cycle}"))

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created {created_count} KPI cycles for {company.name}."
            )
        )
