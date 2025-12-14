from django import template

register = template.Library()

SUPERVISOR_MENU_PERMISSIONS = {

    'modul3': {
        'm3onboarding:organization_chart',
        'm3onboarding:struktur_organisasi',
    },
    'inbox': {
        'inbox:thread_list',
    },
    'modul6': {
        'compensation6:absensi_harian',
        'compensation6:riwayat_absensi',
        'compensation6:payslip_select',
        'compensation6:work_calendar',
    },
}

EMPLOYEE_MENU_PERMISSIONS = {
    'modul6': {
        'compensation6:riwayat_absensi',
        'compensation6:payslip_select',
    }
}


def _callable_attr(obj, name):
    attr = getattr(obj, name, False)
    return attr() if callable(attr) else attr


def _merge_permissions(target, source):
    for module_id, urls in source.items():
        target.setdefault(module_id, set()).update(urls)


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
        {'label': '. Onboarding', 'id': 'modul3', 'sub': [
            {'label': 'Tabel Struktur Mitra', 'url': 'm3onboarding:struktur_organisasi'},
            {'label': 'Struktur Mitra', 'url': 'm3onboarding:organization_chart'},
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
        {'label': '. Kompensasi', 'id': 'modul6', 'sub': [
            {"label": "Payroll Period", "url": "compensation6:payroll_period_list"},
            {"label": "Komponen Gaji", "url": "compensation6:komponen_gaji"},
            {"label": "Absensi Pemborong", "url": "compensation6:absensi_harian"},
            {"label": "Riwayat Absensi", "url": "compensation6:riwayat_absensi"},
            {"label": "Pengajuan Cuti", "url": "compensation6:pengajuan_cuti"},
            {"label": "Slip Borongan", "url": "compensation6:payslip_select"},
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
        {'label': 'Inbox', 'id': 'inbox', 'sub': [
            {'label': 'Percakapan', 'url': 'inbox:thread_list'},
        ]},
    ]

    is_owner = _callable_attr(user, 'is_owner')
    person = getattr(user, 'person', None)
    
    # Supervisor = person has subordinates = True
    # Employee = person has subordinates = False  
    is_supervisor = bool(person and person.subordinates.exists())
    is_employee = bool(person and not person.subordinates.exists())

    role_permissions = {}
    if not is_owner:
        if is_supervisor:
            _merge_permissions(role_permissions, SUPERVISOR_MENU_PERMISSIONS)
        if is_employee:
            _merge_permissions(role_permissions, EMPLOYEE_MENU_PERMISSIONS)

    result = []
    for item in menu_items:
        sub_items = item.get('sub', [])
        filtered_subs = [sub for sub in sub_items if 'perm' not in sub or user.has_perm(sub['perm'])]

        if not filtered_subs:
            continue

        if not is_owner:
            allowed_urls = role_permissions.get(item['id'])
            if not allowed_urls:
                continue
            filtered_subs = [sub for sub in filtered_subs if sub['url'] in allowed_urls]

        if filtered_subs:
            result.append({**item, 'sub': filtered_subs})

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
