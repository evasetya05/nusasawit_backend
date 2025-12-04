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
        
        if hasattr(current_user, 'consultant_profile'):
             return redirect('consultation:consultant_dashboard')

        if hasattr(current_user, 'tip_contributor_profile'):
             return redirect('tips:tip_contributor_dashboard')
        
        # Debug: Show user role information
        person = getattr(current_user, 'person', None)
        is_supervisor = bool(person and person.subordinates.exists())
        
        print(f"DEBUG: User {current_user.username} logged in")
        print(f"DEBUG: is_owner: {current_user.is_owner()}")
        print(f"DEBUG: is_employee: {current_user.is_employee}")
        print(f"DEBUG: person exists: {person is not None}")
        print(f"DEBUG: is_supervisor: {is_supervisor}")
        print(f"DEBUG: company: {current_user.company}")
        print(f"DEBUG: company owner: {current_user.company.owner if current_user.company else None}")
        if person:
            print(f"DEBUG: person name: {person.name}")
            print(f"DEBUG: person has subordinates: {person.subordinates.exists()}")
            print(f"DEBUG: subordinate count: {person.subordinates.count()}")
        
        if current_user.is_owner:
            return render(request, 'dashboard/hr-dashboard.html')

        elif current_user.is_employee:
            jobs = Jobs.objects.filter(team_lead=request.user)
            applications = Application.objects.filter(job_id__in=jobs)
            return render(request, 'dashboard/tl-dashboard.html',
                          context={'jobs': jobs.all(), 'applications': applications})

    return render(request, 'dashboard/i-dashboard.html', context={'jobs': jobs.all(), 
                                                                   'debug_user': request.user if request.user.is_authenticated else None,
                                                                   'debug_is_owner': request.user.is_owner() if request.user.is_authenticated else False,
                                                                   'debug_is_employee': request.user.is_employee() if request.user.is_authenticated else False,
                                                                   'debug_person': getattr(request.user, 'person', None) if request.user.is_authenticated else None,
                                                                   'debug_is_supervisor': bool(getattr(request.user, 'person', None) and getattr(request.user, 'person', None).subordinates.exists()) if request.user.is_authenticated else False})


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
