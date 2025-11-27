from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import Employee  # pastikan app core sudah punya model Employee


class PayrollPeriod(models.Model):
    # company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    month = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="Masukkan angka 1–12 untuk bulan"
    )
    year = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        help_text="Masukkan tahun antara 2000–2100"
    )
    is_closed = models.BooleanField(default=False)
    start_date = models.DateField(
        help_text="Tanggal awal periode penggajian"
    )
    end_date = models.DateField(
        help_text="Tanggal akhir periode penggajian"
    )

    class Meta:
        unique_together = ('month', 'year')

    def __str__(self):
        return f"{self.month:02d}/{self.year}" if not self.start_date or not self.end_date else f"{self.start_date:%d %b %Y} – {self.end_date:%d %b %Y}"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({
                'end_date': 'Tanggal akhir tidak boleh lebih awal dari tanggal awal.'
            })


class Allowance(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.employee}"


class Deduction(models.Model):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.employee}"


class Payroll(models.Model):
    # company = models.ForeignKey('core.Company', on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, null=True, blank=True)

    # ✅ Tambahan field untuk gaji pokok
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    total_allowance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Kontribusi Perusahaan (BPJS) - auto-filled sesuai peraturan Indonesia, bisa diubah owner
    tk_jkk_company = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # JKK Perusahaan
    tk_jkm_company = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # JKM Perusahaan
    tk_jht_company = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # JHT Perusahaan
    tk_jp_company = models.DecimalField(max_digits=12, decimal_places=2, default=0)   # JP Perusahaan
    jkn_company = models.DecimalField(max_digits=12, decimal_places=2, default=0)     # BPJS Kesehatan Perusahaan

    created_at = models.DateTimeField(default=timezone.now)

    def calculate_totals(self):
        # Hitung total allowance dan deduction berdasarkan employee
        self.total_allowance = sum(
            a.amount for a in Allowance.objects.filter(employee=self.employee)
        )
        self.total_deduction = sum(
            d.amount for d in Deduction.objects.filter(employee=self.employee)
        )
        # ✅ Total gaji bersih = gaji pokok + tunjangan - potongan
        self.net_salary = self.basic_salary + self.total_allowance - self.total_deduction
        self.save()

    def __str__(self):
        return f"{self.employee} - {self.period}"


class BPJSConfig(models.Model):
    """Konfigurasi persentase BPJS untuk potongan karyawan dan kontribusi perusahaan.
    Nilai disimpan dalam persen (mis. 2.0 artinya 2%).
    """
    # Potongan Karyawan (BPJS TK & Kesehatan)
    emp_jkk_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # JKK Karyawan
    emp_jkm_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # JKM Karyawan
    emp_jht_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # JHT Karyawan
    emp_jp_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)   # JP/Pensiun Karyawan
    emp_jkn_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # BPJS Kesehatan Karyawan

    # Kontribusi Perusahaan (BPJS TK & Kesehatan)
    com_jkk_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # JKK Perusahaan
    com_jkm_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # JKM Perusahaan
    com_jht_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # JHT Perusahaan
    com_jp_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)   # JP Perusahaan
    com_jkn_pct = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # BPJS Kesehatan Perusahaan

    # Konfigurasi Payroll
    working_days_per_month = models.PositiveSmallIntegerField(default=30, help_text="Hari kerja per bulan")
    overtime_rate = models.DecimalField(max_digits=3, decimal_places=2, default=1.5, help_text="Rate lembur (mis. 1.5 untuk 150%)")

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "BPJSConfig (Persentase)"


class Attendance(models.Model):
    """Model untuk tracking absensi harian karyawan."""
    class Status(models.TextChoices):
        PRESENT = 'present', 'Hadir'
        LATE = 'late', 'Terlambat'
        ABSENT = 'absent', 'Tidak Hadir'
        HALF_DAY = 'half_day', 'Setengah Hari'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    clock_in = models.TimeField(null=True, blank=True)
    clock_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"


class LeaveRequest(models.Model):
    """Model untuk pengajuan cuti secara hirarki."""
    class Status(models.TextChoices):
        PENDING = 'pending', 'Menunggu Approval'
        APPROVED_SUPERVISOR = 'approved_supervisor', 'Disetujui Supervisor'
        APPROVED_HR = 'approved_hr', 'Disetujui HR'
        REJECTED = 'rejected', 'Ditolak'

    class LeaveType(models.TextChoices):
        ANNUAL = 'annual', 'Cuti Tahunan'
        SICK = 'sick', 'Cuti Sakit'
        MATERNITY = 'maternity', 'Cuti Melahirkan'
        OTHER = 'other', 'Lainnya'

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices, default=LeaveType.ANNUAL)
    reason = models.TextField()
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    approved_by_supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='supervisor_approvals')
    approved_by_hr = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='hr_approvals')
    approval_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.start_date} to {self.end_date})"
