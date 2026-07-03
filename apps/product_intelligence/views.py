from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .serializers import BarcodeLookupRequestSerializer
from .services import ProductLookupService

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class ProductIntelligenceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=BarcodeLookupRequestSerializer,
        responses={200: OpenApiTypes.OBJECT},
        tags=["Product Intelligence"]
    )
    @action(detail=False, methods=['post'], url_path='lookup-barcode')
    def lookup_barcode(self, request):
        serializer = BarcodeLookupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        barcode = serializer.validated_data['barcode']
        store_id = serializer.validated_data.get('store_id') or request.query_params.get('store_id')

        if not store_id:
            from apps.accounts.models import StoreMembership
            membership = StoreMembership.objects.filter(user=request.user).first()
            if membership:
                store_id = membership.store_id
        
        if not store_id:
            return Response(
                {"error": "store_id is required either in body, query params, or associated to user."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        result = ProductLookupService.lookup_by_barcode(barcode, str(store_id))
        return Response(result, status=status.HTTP_200_OK)
