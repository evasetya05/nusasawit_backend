from django import template

register = template.Library()


@register.simple_tag
def create_menu(user):
    menu_items = [
        {'label': '1. Perencanaan Tenaga Kerja', 'id': 'modul1', 'sub': [
            {'label':'Dashboard LCR', 'url': 'm1planning:dashboard'},
            {'label':'Rasio Biaya Karyawan', 'url': 'm1planning:list'},
            
        ]},
        {'label': '2. Rekrutmen dan Seleksi', 'id': 'modul2', 'sub': [
            {'label': 'Dashboard', 'url': 'recruit_dashboard'},
            {'label': 'Link Kandidat', 'url': 'generate_link'},
            {'label': 'Matrix Interview', 'url': 'pertanyaan_interviews'},
        ]},
        {'label': '3. Onboarding', 'id': 'modul3', 'sub': [
            {'label': 'Struktur Organisasi', 'url': 'm3onboarding:struktur_organisasi'},
            {'label': 'Dokumen Standar', 'url': 'm3onboarding:document'},
        ]},
        {'label': '4. Manajemen Kinerja', 'id': 'modul4', 'sub': [
            {'label': 'Dashboard KPI', 'url': 'kinerja4:dashboard'},
            {'label': 'Daftar KPI', 'url': 'kinerja4:kpi_list'},
            {'label': 'Buat Siklus KPI', 'url': 'kinerja4:cycle_create', 'perm': 'kinerja4.add_kpiperiodtarget'},
        ]},
        {'label': '5. Pengembangan Karyawan', 'id': 'modul5', 'sub': [
            {"label": "Analisis Kebutuhan Pelatihan", "url": "learning5:trainingneed_list"},
            {"label": "Kompetensi", "url": "learning5:competency_add"},
        ]},
        {'label': '6. Kompensasi', 'id': 'modul6', 'sub': [
            {"label": "Payroll Period", "url": "compensation6:payroll_period_list"},
            {"label": "Komponen Gaji", "url": "compensation6:komponen_gaji"},
            {"label": "Absensi Harian", "url": "compensation6:absensi_harian"},
            {"label": "Pengajuan Cuti", "url": "compensation6:pengajuan_cuti"},
            {"label": "Slip Gaji", "url": "compensation6:payslip_select"},
            {"label": "Kalender", "url": "compensation6:work_calendar"}
        ]},
        {'label': '7. Industrial Relation', 'id': 'modul8', 'sub': [
            {'label':'Complaint', 'url': 'ir8:complaint_list'},
        ]},
        {'label': '8. Continues Improvement', 'id': 'modul9', 'sub': [
            {'label':'OCAI', 'url': 'm9improvement:dashboard'},
            {'label':'Link Test OCAI', 'url': 'm9improvement:ocai_form'},
            {'label':'Hasil Test OCAI', 'url': 'm9improvement:result_ocai'},
        ]},
    ]

    result = []
    for item in menu_items:
        if 'sub' in item:
            item['sub'] = [sub for sub in item['sub'] if 'perm' not in sub or user.has_perm(sub['perm'])]
            if item['sub']:
                result.append(item)
        else:
            result.append(item)

    return result


@register.simple_tag
def create_hr_menu():
    return [
        {'label': 'Add Job', 'url': 'jobs:create-job'},
        {'label': 'All Users', 'url': 'user:list'},
        {'label': 'Create Blog', 'url': 'blog:create_blog'},
    ]


@register.simple_tag
def create_owner_menu():
    return [
        {'label': 'Company Profile', 'url': 'company:profile'},
        {'label': 'Departments', 'url': 'company:department'},
        {'label': 'Positions', 'url': 'company:position'},
    ]


@register.filter
def is_owner(user):
    return user.is_owner


@register.filter
def is_employee(user):
    return user.is_employee


@register.filter
def is_active(url, match):
    return ' active' if url.startswith(match) else ''
