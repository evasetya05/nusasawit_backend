from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Tip, TipContributor, TipDiscussion
from .serializers import TipSerializer, TipContributorSerializer, TipDiscussionSerializer
from api.permission import HasValidAppKey

@api_view(['GET', 'POST'])
@permission_classes([HasValidAppKey])
def tips_list(request):
    if request.method == 'GET':
        tips = Tip.objects.all().order_by('-created_at')
        serializer = TipSerializer(tips, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Get user identifier from request headers
        user_identifier = getattr(request, 'user_identifier', None)
        if user_identifier:
            request.data['discussion'] = user_identifier
        
        serializer = TipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'POST'])
@permission_classes([HasValidAppKey])
def contributors_list(request):
    if request.method == 'GET':
        contributors = TipContributor.objects.all()
        serializer = TipContributorSerializer(contributors, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = TipContributorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'POST'])
@permission_classes([HasValidAppKey])
def tip_discussions(request, tip_id):
    if request.method == 'GET':
        discussions = TipDiscussion.objects.filter(tip_id=tip_id)
        serializer = TipDiscussionSerializer(discussions, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        # Get user identifier from request headers
        user_identifier = getattr(request, 'user_identifier', None)
        
        # If no user_identifier, try to get it from headers directly
        if not user_identifier:
            email = request.headers.get('X-EMAIL')
            phone = request.headers.get('X-PHONE')
            
            if email and phone:
                user_identifier = f"{email}|{phone}"
            elif email:
                user_identifier = email
            elif phone:
                user_identifier = phone
            else:
                user_identifier = "unknown"
        
        # Create data with user_identifier
        discussion_data = {
            'tip': tip_id,
            'message': request.data.get('message', ''),
            'user_identifier': user_identifier
        }
        
        serializer = TipDiscussionSerializer(data=discussion_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

