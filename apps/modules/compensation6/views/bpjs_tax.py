from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
from apps.core.models import Employee
from ..models import Payroll, PayrollPeriod, Allowance, Deduction, BPJSConfig, Attendance, LeaveRequest
from ..forms import (
    AllowanceForm, DeductionForm, PayrollPeriodForm,
    BPJSTKForm, BPJSTKJPForm, BPJSKesehatanForm, PajakForm,
    BPJSTKJKKCompanyForm, BPJSTKJKMCompanyForm, BPJSTKJHTCompanyForm, BPJSTKJPCompanyForm, BPJSKesehatanCompanyForm,
    BPJSConfigKaryawanForm, BPJSConfigPerusahaanForm,
    PayslipSelectionForm,
    AttendanceForm, LeaveRequestForm
)
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import render_to_string




def add_bpjs_tk_jht(request):
    form = BPJSTKForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JHT Karyawan'
        deduction.save()
        messages.success(request, 'BPJS TK - JHT Karyawan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jht.html', {'form': form})


def add_bpjs_tk_jp(request):
    form = BPJSTKJPForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JP Karyawan'
        deduction.save()
        messages.success(request, 'BPJS TK - JP Karyawan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jp.html', {'form': form})


def add_bpjs_kesehatan(request):
    form = BPJSKesehatanForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS Kesehatan Karyawan'
        deduction.save()
        messages.success(request, 'BPJS Kesehatan Karyawan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_kesehatan.html', {'form': form})


def add_pajak(request):
    form = PajakForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'Pajak Penghasilan'
        deduction.save()
        messages.success(request, 'Pajak Penghasilan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_pajak.html', {'form': form})


def add_bpjs_tk_jkk_company(request):
    form = BPJSTKJKKCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JKK Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS TK - JKK Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jkk_company.html', {'form': form})


def add_bpjs_tk_jkm_company(request):
    form = BPJSTKJKMCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JKM Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS TK - JKM Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jkm_company.html', {'form': form})


def add_bpjs_tk_jht_company(request):
    form = BPJSTKJHTCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JHT Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS TK - JHT Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jht_company.html', {'form': form})


def add_bpjs_tk_jp_company(request):
    form = BPJSTKJPCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS TK - JP Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS TK - JP Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_tk_jp_company.html', {'form': form})


def add_bpjs_kesehatan_company(request):
    form = BPJSKesehatanCompanyForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        deduction = form.save(commit=False)
        deduction.name = 'BPJS Kesehatan Perusahaan'
        deduction.save()
        messages.success(request, 'BPJS Kesehatan Perusahaan berhasil ditambahkan.')
        return redirect('compensation6:komponen_gaji')
    return render(request, 'compensation6/add_bpjs_kesehatan_company.html', {'form': form})


def bpjs_karyawan(request):
    cfg, _ = BPJSConfig.objects.get_or_create(id=1)
    form = BPJSConfigKaryawanForm(request.POST or None, instance=cfg)
    if request.method == 'POST':
        # Hanya owner yang boleh update
        if not getattr(request.user, 'is_owner', False):
            messages.error(request, 'Hanya owner yang dapat mengubah persentase BPJS karyawan.')
            return redirect('compensation6:bpjs_karyawan')
        if form.is_valid():
            form.save()
            messages.success(request, 'Persentase BPJS karyawan berhasil disimpan.')
            return redirect('compensation6:bpjs_karyawan')
    return render(request, "compensation6/bpjs_karyawan.html", {'form': form, 'cfg': cfg})


def bpjs_perusahaan(request):
    cfg, _ = BPJSConfig.objects.get_or_create(id=1)
    form = BPJSConfigPerusahaanForm(request.POST or None, instance=cfg)
    if request.method == 'POST':
        # Hanya owner yang boleh update
        if not getattr(request.user, 'is_owner', False):
            messages.error(request, 'Hanya owner yang dapat mengubah persentase BPJS perusahaan.')
            return redirect('compensation6:bpjs_perusahaan')
        if form.is_valid():
            form.save()
            messages.success(request, 'Persentase BPJS perusahaan berhasil disimpan.')
            return redirect('compensation6:bpjs_perusahaan')
    return render(request, "compensation6/bpjs_perusahaan.html", {'form': form, 'cfg': cfg})

