from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from api.permission import HasValidAppKey
from .models import CertificationScheme


class FlutterCertificationListView(APIView):
    permission_classes = [HasValidAppKey]
    
    def get(self, request):
        flutter_user = getattr(request, 'flutter_user', None)
        if not flutter_user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all certification schemes
        schemes = CertificationScheme.objects.all()
        
        # Create simple response
        result = []
        for scheme in schemes:
            scheme_data = {
                'id': scheme.id,
                'name': scheme.name,
                'description': scheme.description,
                'user_status': 'not_started',  # Default status since we don't have progress tracking
                'has_progress': False,
            }
            result.append(scheme_data)
        
        return Response({
            'user_identifier': flutter_user.identifier,
            'certifications': result
        })


class FlutterCertificationDetailView(APIView):
    permission_classes = [HasValidAppKey]
    
    def get(self, request, pk):
        flutter_user = getattr(request, 'flutter_user', None)
        if not flutter_user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            scheme = CertificationScheme.objects.get(id=pk)
        except CertificationScheme.DoesNotExist:
            return Response({"error": "Certification not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get scheme details
        details = scheme.details.all() if hasattr(scheme, 'details') else []
        
        scheme_data = {
            'id': scheme.id,
            'name': scheme.name,
            'description': scheme.description,
            'user_status': 'not_started',
            'has_progress': False,
            'details': [
                {
                    'id': detail.id,
                    'title': detail.title,
                    'description': detail.description,
                }
                for detail in details
            ]
        }
        
        return Response({
            'user_identifier': flutter_user.identifier,
            'certification': scheme_data
        })
