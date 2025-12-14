from django.urls import path
from .views import penggajian, bpjs_tax, payslip, absensi, cuti
from .views.calendar import approve_work_request, reject_work_request

app_name = 'compensation6'

urlpatterns = [
    path('', penggajian.compensation_dashboard, name='compensation_dashboard'),
    path('allowance/add/', penggajian.add_allowance, name='add_allowance'),
    path('deduction/add/', penggajian.add_deduction, name='add_deduction'),
    path('periods/', penggajian.payroll_period_list, name='payroll_period_list'),
    path('periods/<int:period_id>/generate/', penggajian.generate_payroll, name='generate_payroll'),
    path('periods/<int:period_id>/close/', penggajian.close_period, name='close_period'),
    path('payrolls/', penggajian.payroll_list, name='payroll_list'),
    path('payrolls/<int:pk>/', penggajian.payroll_detail, name='payroll_detail'),
    path("komponen-gaji/", penggajian.komponen_gaji_view, name="komponen_gaji"),
    path('bpjs-tk-jht/add/', bpjs_tax.add_bpjs_tk_jht, name='add_bpjs_tk_jht'),
    path('bpjs-tk-jp/add/', bpjs_tax.add_bpjs_tk_jp, name='add_bpjs_tk_jp'),
    path('bpjs-kesehatan/add/', bpjs_tax.add_bpjs_kesehatan, name='add_bpjs_kesehatan'),
    path('pajak/add/', bpjs_tax.add_pajak, name='add_pajak'),
    path('bpjs-tk-jkk-company/add/', bpjs_tax.add_bpjs_tk_jkk_company, name='add_bpjs_tk_jkk_company'),
    path('bpjs-tk-jkm-company/add/', bpjs_tax.add_bpjs_tk_jkm_company, name='add_bpjs_tk_jkm_company'),
    path('bpjs-tk-jht-company/add/', bpjs_tax.add_bpjs_tk_jht_company, name='add_bpjs_tk_jht_company'),
    path('bpjs-tk-jp-company/add/', bpjs_tax.add_bpjs_tk_jp_company, name='add_bpjs_tk_jp_company'),
    path('bpjs-kesehatan-company/add/', bpjs_tax.add_bpjs_kesehatan_company, name='add_bpjs_kesehatan_company'),
    path('bpjs-karyawan/', bpjs_tax.bpjs_karyawan, name='bpjs_karyawan'),
    path('bpjs-perusahaan/', bpjs_tax.bpjs_perusahaan, name='bpjs_perusahaan'),
   
    # payslip
    path('payslip/', payslip.payslip_select, name='payslip_select'),
    path('payslip/<int:employee_id>/<int:month>/<int:year>/', payslip.payslip_preview, name='payslip_preview'),
    path('payslip/<int:employee_id>/<int:month>/<int:year>/pdf/', payslip.payslip_pdf, name='payslip_pdf'),
   
    # absensi and cuti
    path('absensi-harian/', absensi.absensi_harian, name='absensi_harian'),
    path('riwayat-absensi/', absensi.riwayat_absensi, name='riwayat_absensi'),
    path('api/get-borongan-by-employee/', absensi.get_borongan_by_employee, name='get_borongan_by_employee'),
    path('work-calendar/', absensi.WorkCalendarView.as_view(), name='work_calendar'),
    path('work-request/<int:work_request_id>/approve/', approve_work_request, name='approve-work-request'),
    path('work-request/<int:work_request_id>/reject/', reject_work_request, name='reject-work-request'),
    path('pengajuan-cuti/', cuti.pengajuan_cuti, name='pengajuan_cuti'),
    path('leave-approvals/', cuti.leave_approvals, name='leave_approvals'),
    path('leave-approve/<int:leave_id>/<str:action>/', cuti.approve_leave, name='approve_leave'),
]
