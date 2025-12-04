from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator

from apps.core.models import Employee, Borongan  # pastikan app core sudah punya model Employee


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
    
    # Store borongan dates info as JSON for display purposes
    borongan_dates = models.JSONField(default=list, blank=True, help_text="List of dates when borongan was recorded")

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
        # Hitung total allowance dan deduction berdasarkan employee DAN period
        self.total_allowance = sum(
            a.amount for a in Allowance.objects.filter(employee=self.employee, period=self.period)
        )
        self.total_deduction = sum(
            d.amount for d in Deduction.objects.filter(employee=self.employee, period=self.period)
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
    
    # Borongan reference (optional) - dari employee.borongan
    borongan = models.ForeignKey(Borongan, on_delete=models.SET_NULL, null=True, blank=True, help_text="Pilih pekerjaan borongan (opsional)")
    realisasi = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)], help_text="Jumlah realisasi borongan (dalam satuan)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_hasil_akhir(self):
        """Hitung hasil akhir = realisasi × harga_borongan"""
        if self.borongan and self.realisasi:
            return Decimal(self.realisasi) * Decimal(self.borongan.harga_borongan)
        return Decimal('0')

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.status})"


class WorkRequest(models.Model):
    """Permintaan penugasan kerja per karyawan."""

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="work_requests",
    )
    start_date = models.DateField(help_text="Tanggal mulai penugasan kerja", null=True, blank=True)
    end_date = models.DateField(help_text="Tanggal akhir penugasan kerja", null=True, blank=True)
    due_date = models.DateField(help_text="Tanggal batas pengerjaan", null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Tracking fields
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_work_requests",
        help_text="User yang membuat permintaan kerja"
    )
    flutter_user = models.ForeignKey(
        "user_flutter.FlutterUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_requests",
        help_text="Referensi user Flutter yang membuat permintaan"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date", "employee__name"]
        unique_together = ['employee', 'start_date', 'end_date']

    def __str__(self):
        if self.start_date == self.end_date:
            return f"{self.employee} - {self.start_date:%d %b %Y}" if self.employee else f"WorkRequest {self.start_date}"
        else:
            return f"{self.employee} - {self.start_date:%d %b %Y} to {self.end_date:%d %b %Y}" if self.employee else f"WorkRequest {self.start_date} to {self.end_date}"

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": "Tanggal akhir tidak boleh sebelum tanggal mulai."})
        if self.due_date and self.start_date and self.due_date < self.start_date:
            raise ValidationError({"due_date": "Due date tidak boleh sebelum tanggal mulai kerja."})

    @property
    def is_editable(self):
        today = timezone.now().date()
        return self.end_date >= today

    def covers_date(self, date):
        """Check if this work request covers the given date."""
        return self.start_date <= date <= self.end_date

