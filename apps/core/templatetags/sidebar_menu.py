from django import template

register = template.Library()


@register.simple_tag
def create_menu(user):
    menu_items = [
        {'label': '1. Perencanaan Tenaga Kerja', 'url': 'planing1_dashboard'},
        {'label': '2. Rekrutmen dan Seleksi', 'url': 'recruit_dashboard', 'sub': [
            {'label': '2.A Link untuk Kandidat', 'url': 'generate_link'},
            {'label': '2.B Matrix Interview', 'url': 'pertanyaan_interviews'},
            {'label': '2.C Hasil Test Big 5 Personality', 'url': 'personality_test_result'},
            {'label': '2.D Hasil DOPE Tes', 'url': 'dope_test_result'},
            {'label': '2.E Hasil Interview', 'url': 'interviews'},
        ]},
        {'label': '3. Onboarding', 'url': 'm3onboarding:dashboard', 'sub': [
            {'label': '3.A Standar SOP', 'url': 'm3onboarding:sop'},
            {'label': '3.B Struktur Organisasi', 'url': 'm3onboarding:struktur_organisasi'},
            {'label': '3.C Saran untuk Perusahaan', 'url': 'm3onboarding:saran_perusahaan'},
            {'label': '3.D Rencana Training', 'url': 'm3onboarding:rencana_training'},
        ]},
        {'label': '4. Manajemen Kinerja', 'url': 'kinerja4_dashboard'},
        {'label': '5. Pengembangan Karyawan', 'url': 'learning5_dashboard'},
        {'label': '6. Kesejahteraan dan Retensi', 'url': 'compensation6_dashboard'},
        {'label': '7. Administrasi dan Kepatuhan', 'url': 'compliance_dashboard'},
        {'label': '8. Industrial Relation', 'url': 'industrial_relation_dashboard'},
        {'label': '9. Continues Improvement', 'url': 'm9improvement:dashboard', 'sub': [
            {'label':'9.A Link Test OCAI', 'url': 'm9improvement:ocai_form'},
            {'label':'9.B Hasil Test OCAI', 'url': 'm9improvement:result_ocai'},
        ]},
    ]

    return menu_items


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
    return user.is_owner()


@register.filter
def is_employee(user):
    return user.is_employee()


@register.filter
def is_active(url, match):
    return ' active' if url.startswith(match) else ''
