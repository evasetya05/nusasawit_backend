import json
import os
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "HEAD"])
def assetlinks(request):
    """
    Serve .well-known/assetlinks.json file
    """
    assetlinks_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        '.well-known', 
        'assetlinks.json'
    )
    
    try:
        with open(assetlinks_path, 'r') as f:
            data = json.load(f)
        return JsonResponse(data, safe=False)
    except FileNotFoundError:
        return JsonResponse(
            {'error': 'assetlinks.json not found'}, 
            status=404
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'Invalid JSON in assetlinks.json'}, 
            status=500
        )
