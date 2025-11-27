from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages

from apps.extras.job.models import Jobs, Application
from apps.core.services.payment_services import (
    get_pro_modules,
    calculate_order_details,
    create_order_in_database,
    confirm_payment_submission,
)


def index(request):
    jobs = Jobs.objects

    if request.user.is_authenticated:
        current_user = request.user
        if current_user.is_owner:
            return render(request, 'dashboard/hr-dashboard.html')

        elif current_user.is_employee:
            jobs = Jobs.objects.filter(team_lead=request.user)
            applications = Application.objects.filter(job_id__in=jobs)
            return render(request, 'dashboard/tl-dashboard.html',
                          context={'jobs': jobs.all(), 'applications': applications})

    return render(request, 'dashboard/i-dashboard.html', context={'jobs': jobs.all()})


def pricing(request):
    return render(request, 'dashboard/pricing.html')


def checkout(request):
    """
    Render the checkout page for the Pro plan with selectable modules.
    Base price is Rp50.000, and each module has an additional price.
    """
    context = {
        "base_price": 50000,
        "modules": get_pro_modules(),
    }
    return render(request, 'dashboard/checkout.html', context)

@login_required
def payment(request):
    user = request.user
    if request.method == 'POST' and request.POST.get('confirm_payment'):
        # User clicks "I Have Paid": delegate to service for receipt creation and admin notification
        order_session = request.session.get('current_order')
        if not order_session:
            messages.info(request, 'Silakan lakukan checkout terlebih dahulu.')
            return redirect(reverse('checkout'))

        receipt_file = request.FILES.get('receipt')
        confirm_payment_submission(order_session, user, receipt_file)

        messages.success(request, 'Terima kasih! Pembayaran Anda akan segera kami verifikasi. Anda akan dihubungi setelah berhasil dikonfirmasi.')
        return render(request, 'dashboard/payment_submitted.html', {'order': order_session})

    if request.method == 'POST':
        # Process the order
        order_data = calculate_order_details(request.POST)

        # Save to session (source of truth for this flow)
        request.session['current_order'] = order_data

        # Save to database if user is authenticated
        create_order_in_database(order_data, user)

        return redirect(reverse('payment'))

    # GET: show payment summary
    order = request.session.get('current_order')
    if not order:
        messages.info(request, 'Silakan lakukan checkout terlebih dahulu.')
        return redirect(reverse('checkout'))

    return render(request, 'dashboard/payment.html', { 'order': order })
