from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Tip
from .serializers import TipSerializer
from api.permission import HasValidAppKey

@api_view(['GET'])
@permission_classes([HasValidAppKey])
def tips_list(request):
    tips = Tip.objects.all().order_by('-created_at')
    serializer = TipSerializer(tips, many=True)
    return Response(serializer.data)


