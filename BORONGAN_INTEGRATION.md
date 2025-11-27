# Integrasi Borongan ke Modul Kompensasi (compensation6)

## Ringkasan
Borongan (piece rate compensation) dari `apps.core.employee` telah diintegrasikan ke dalam sistem generate payroll pada modul `compensation6`. Setiap borongan karyawan akan otomatis ditambahkan sebagai **allowance** ketika payroll di-generate.

## Perubahan yang Dilakukan

### 1. File: `apps/modules/compensation6/views/penggajian.py`

#### Function: `generate_payroll(request, period_id)`
Ditambahkan kode untuk memproses borongan pada bagian setelah tunjangan tetap:

```python
# Create borongan allowances from employee's borongan records
borongan_records = emp.borongan.all()
for borongan in borongan_records:
    # Create allowance for each borongan
    allowance_name = f"Borongan: {borongan.pekerjaan}"
    if not Allowance.objects.filter(
        employee=emp,
        period=period,
        name=allowance_name
    ).exists():
        Allowance.objects.create(
            employee=emp,
            period=period,
            name=allowance_name,
            amount=borongan.harga_borongan
        )
```

**Penjelasan:**
- Mengambil semua borongan records untuk setiap karyawan via `emp.borongan.all()`
- Untuk setiap borongan, membuat allowance dengan nama format `"Borongan: {pekerjaan}"`
- Menggunakan `harga_borongan` dari model Borongan sebagai amount allowance
- Menggunakan `get_or_create` pattern untuk menghindari duplikasi

## Alur Data

```
Employee.borongan (apps.core)
    ↓
generate_payroll view
    ↓
Allowance.objects.create()
    ↓
Payroll.calculate_totals()
    ├─ total_allowance += sum(allowances)
    ├─ net_salary = basic_salary + total_allowance - total_deduction
    └─ Ditampilkan di:
       ├─ payroll_detail.html
       ├─ payslip_pdf.html
       └─ payslip_preview
```

## Contoh Penggunaan

### Skenario 1: Employee dengan Borongan
```
Employee: John Doe
- Gaji Pokok: Rp 1.000.000
- Borongan 1: pupuk (karung) @ Rp 1.000
- Borongan 2: Menggali tanah (meter kubik) @ Rp 50.000

Saat generate_payroll:
- Allowance 1: "Tunjangan Tetap" = Rp 100.000
- Allowance 2: "Borongan: pupuk" = Rp 1.000
- Allowance 3: "Borongan: Menggali tanah" = Rp 50.000
- Total Allowance = Rp 151.000
- Net Salary = Rp 1.000.000 + Rp 151.000 - (potongan) = Rp 1.151.000 - (potongan)
```

## Poin Penting

1. **Tidak ada perubahan model** - Models tetap sama, hanya menambah logika di views
2. **Automatic inclusion** - Borongan otomatis ditambahkan saat `generate_payroll` dipanggil
3. **Idempotent** - Menggunakan `get_or_create` untuk menghindari duplikasi
4. **Tampilan di Payslip** - Borongan akan tampil di:
   - Payroll Detail page (dalam tabel "Rincian Tunjangan")
   - Payslip PDF/Preview (dalam tabel "Tunjangan & Lembur")

## Testing

Untuk test integrasi:

```python
from apps.core.models import Employee, Borongan
from apps.modules.compensation6.models import PayrollPeriod, Payroll, Allowance

# Setup test data
employee = Employee.objects.first()
borongan = Borongan.objects.create(
    employee=employee,
    pekerjaan="Test Borongan",
    satuan="unit",
    harga_borongan=100000
)

period = PayrollPeriod.objects.create(month=1, year=2025, ...)

# Generate payroll
payroll = Payroll.objects.create(employee=employee, period=period)

# Check allowances
allowances = Allowance.objects.filter(employee=employee, period=period)
# Should include "Borongan: Test Borongan" with amount 100000
```

## Future Enhancements

- [ ] Add UI untuk manage borongan dari compensation6 module
- [ ] Add reporting untuk total borongan per period
- [ ] Add validation untuk harga_borongan
- [ ] Add history tracking untuk borongan changes

## Notes

- Borongan ditambahkan sebagai **allowance** (bukan salary component terpisah)
- Ini memastikan otomatis termasuk dalam `net_salary` calculation
- Payroll harus di-regenerate jika ada perubahan borongan setelah period sudah dibuat

