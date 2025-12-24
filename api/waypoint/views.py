import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils.http import urlencode


def waypoint_deep_link(request: HttpRequest) -> HttpResponse:
    """Render intermediate page to open waypoint in the NusaSawit app."""

    encoded_waypoint = request.GET.get("waypoint")
    app_scheme = "nusasawit"
    fallback_url = "https://play.google.com/store/apps/details?id=com.nusasawit.app"

    if encoded_waypoint:
        deep_link_url = f"{app_scheme}://peta?{urlencode({'waypoint': encoded_waypoint})}"
    else:
        deep_link_url = f"{app_scheme}://peta"

    debug_mode = request.GET.get("debug") == "1"

    context = {
        "waypoint": encoded_waypoint,
        "app_scheme": app_scheme,
        "app_url": deep_link_url,
        "deep_link_url": deep_link_url,
        "fallback_url": fallback_url,
        "debug_mode": debug_mode,
    }

    if debug_mode:
        logger = logging.getLogger(__name__)
        debug_info = {
            "request_is_secure": request.is_secure(),
            "request_scheme": request.scheme,
            "host": request.get_host(),
            "path": request.get_full_path(),
            "user_agent": request.headers.get("User-Agent"),
            "referer": request.headers.get("Referer"),
            "deep_link_url": deep_link_url,
            "fallback_url": fallback_url,
            "waypoint_present": bool(encoded_waypoint),
        }
        context["debug_info"] = debug_info
        logger.info("waypoint deep link debug", extra={"debug": debug_info})

    return render(request, "api/waypoint/deep_link.html", context)
