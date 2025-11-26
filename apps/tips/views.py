from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Tip
from .serializers import TipSerializer

@api_view(['GET'])
def tips_list(request):
    tips = Tip.objects.all().order_by('-created_at')
    serializer = TipSerializer(tips, many=True)
    return Response(serializer.data)
