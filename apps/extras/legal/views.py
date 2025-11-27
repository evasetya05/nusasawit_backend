from django.shortcuts import render
from .models import Policy
from django.http import Http404

def privacy_policy(request):
    policy = Policy.objects.filter(
        type=Policy.DocType.PRIVACY_POLICY, is_active=True
    ).first()
    if not policy:
        raise Http404("Privacy policy not found")
    return render(request, "legal/policy.html", {"policy": policy})


def terms_of_service(request):
    terms = Policy.objects.filter(
        type=Policy.DocType.TERMS_OF_SERVICE, is_active=True
    ).first()
    if not terms:
        raise Http404("Terms of service not found")
    return render(request, "legal/policy.html", {"policy": terms})
