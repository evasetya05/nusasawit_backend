from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Tip
from .serializers import TipSerializer

@api_view(['GET'])
def tips_list(request):
    tips = Tip.objects.all().order_by('-created_at')
    serializer = TipSerializer(tips, many=True)
    return Response(serializer.data)



# apps/tips/views.py
from django.http import HttpResponse
import logging

logger = logging.getLogger('django')

def test_log(request):
    logger.error("Ini log test untuk django-error.log di root project")
    return HttpResponse("Log test dicatat")
