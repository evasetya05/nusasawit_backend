from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.utils.http import urlencode


def waypoint_deep_link(request: HttpRequest) -> HttpResponse:
    """Render intermediate page to open waypoint in the NusaSawit app."""

    encoded_waypoint = request.GET.get("waypoint")

    context = {
        "waypoint": encoded_waypoint,
        "app_scheme": "nusasawit",
        "fallback_url": "https://play.google.com/store/apps/details?id=com.nusasawit.app",
    }

    if encoded_waypoint:
        context["app_url"] = f"nusasawit://peta?{urlencode({'waypoint': encoded_waypoint})}"
    else:
        context["app_url"] = "nusasawit://peta"

    return render(request, "api/waypoint/deep_link.html", context)
