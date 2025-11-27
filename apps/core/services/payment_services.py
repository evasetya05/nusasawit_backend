from django.conf import settings
from django.core.mail import send_mail

from apps.core.models.order import Order, PaymentReceipt

def get_pro_modules():
    """Return the list of available professional modules with their prices."""
    return [
        {"key": "planing", "name": "Perencanaan Tenaga Kerja", "price": 15000},
        {"key": "recruit", "name": "Rekrutmen dan Seleksi", "price": 10000},
        {"key": "onboarding", "name": "Onboarding dan Pelatihan", "price": 12000},
        {"key": "kinerja", "name": "Manajemen Kinerja", "price": 18000},
        {"key": "learning", "name": "Pengembangan Karyawan", "price": 14000},
        {"key": "compensation", "name": "Kompensasi & Benefit", "price": 20000},
        {"key": "compliance", "name": "Administrasi & Kepatuhan", "price": 8000},
        {"key": "industrial", "name": "Industrial Relation", "price": 16000},
        {"key": "improvement", "name": "Continues Improvement", "price": 9000},
    ]

def calculate_order_details(request_data, base_price=50000):
    """Calculate order details based on request data and base price.

    Supports billing cycles: monthly (default) or yearly. Yearly total is 12x the
    monthly total (no discount applied by default).
    """
    modules = get_pro_modules()
    modules_by_key = {m["key"]: m for m in modules}

    user_pack_price = int(request_data.get('user_pack') or 0)
    # `request_data` may be a Django QueryDict (supports getlist) or a plain dict
    try:
        selected_keys = request_data.getlist('modules', [])
    except AttributeError:
        sel = request_data.get('modules', [])
        selected_keys = sel if isinstance(sel, list) else [sel] if sel else []

    billing_cycle = (request_data.get('billing_cycle') or 'monthly').lower()
    if billing_cycle not in ('monthly', 'yearly'):
        billing_cycle = 'monthly'

    selected = []
    monthly_total = base_price + user_pack_price

    for key in selected_keys:
        if key in modules_by_key:
            m = modules_by_key[key]
            monthly_total += m['price']
            selected.append({"key": key, "name": m['name'], "price": m['price']})

    # Calculate total based on billing cycle
    if billing_cycle == 'yearly':
        total = monthly_total * 12
    else:
        total = monthly_total

    return {
        'base_price': base_price,
        'user_pack_price': user_pack_price,
        'modules': selected,
        'billing_cycle': billing_cycle,
        'total_price': total,
    }

def create_order_in_database(order_data, user=None):
    """Create an order record in the database if possible."""
    try:
        if user and hasattr(user, 'is_owner') and user.is_owner:
            Order.objects.create(
                user=user,
                company=user.company,
                base_price=order_data['base_price'],
                user_pack_price=order_data['user_pack_price'],
                modules=order_data['modules'],
                billing_cycle=order_data.get('billing_cycle', 'monthly'),
                total_price=order_data['total_price'],
                status='pending',
            )
    except Exception:
        # Silently ignore if DB table doesn't exist or other migration issues
        pass


def confirm_payment_submission(order_session, user, receipt_file=None):
    """
    Create a payment receipt for manual verification and notify admin.

    Returns True on success (or graceful no-op), False on hard failure.
    """
    success = True
    # Link receipt with the most recent order of the company (if available)
    try:
        last_order = Order.objects.filter(company=user.company).order_by('-created_at').first()
        PaymentReceipt.objects.create(
            order=last_order,
            company=user.company,
            user=user,
            receipt_file=receipt_file
        )
    except Exception:
        # Fail silently to avoid breaking UX
        success = False

    # Send email notification to admin (fail silently)
    try:
        admin_email = 'admin@sdmportabel.com'
        subject = f"Konfirmasi Pembayaran Pro - {getattr(user.company, 'name', '-') }"
        full_name = user.get_full_name() if hasattr(user, 'get_full_name') else ''
        body = (
            f"Pengguna: {full_name} ({getattr(user, 'email', '')})\n"
            f"Perusahaan: {getattr(user.company, 'name', '-') }\n"
            f"Total: Rp{order_session.get('total_price')}\n"
            f"Siklus: {order_session.get('billing_cycle')}\n\n"
            "Silakan lakukan verifikasi pembayaran di sistem admin."
        )
        send_mail(
            subject,
            body,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@sdmportabel.com'),
            [admin_email],
            fail_silently=True,
        )
    except Exception:
        pass

    return success
