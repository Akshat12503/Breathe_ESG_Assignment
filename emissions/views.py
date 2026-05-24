from rest_framework import status, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import NormalizedEmissionActivity, AuditTrail

# 1. Serializer (Converts database rows to JSON format cleanly)
class EmissionActivitySerializer(serializers.ModelSerializer):
    source_type = serializers.CharField(source='source_log.source_type', read_only=True)
    filename = serializers.CharField(source='source_log.filename_or_endpoint', read_only=True)

    class Meta:
        model = NormalizedEmissionActivity
        fields = [
            'id', 'scope_category', 'activity_type', 'raw_data_snapshot',
            'raw_quantity', 'raw_unit', 'normalized_quantity_kwh',
            'co2e_emissions_mt', 'review_status', 'flag_reason', 
            'source_type', 'filename', 'reviewed_at'
        ]

# 2. ViewSet (Handles GET requests and Custom POST approvals)
class EmissionActivityViewSet(viewsets.ModelViewSet):
    queryset = NormalizedEmissionActivity.objects.all().order_by('-co2e_emissions_mt')
    serializer_class = EmissionActivitySerializer

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_row(self, request, pk=None):
        """Custom endpoint allowing analysts to sign off and lock entries."""
        activity = self.get_object()
        
        if activity.review_status == 'APPROVED & LOCKED':
            return Response(
                {"error": "This data point is already locked for audit."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Log old status to the audit trail before updating
        old_status = activity.review_status
        activity.review_status = 'APPROVED & LOCKED'
        activity.reviewed_at = timezone.now()
        # Set a fallback user profile for prototype purposes
        activity.reviewed_by = request.user if request.user.is_authenticated else None
        activity.save()

        # Commit to AuditTrail Ledger
        AuditTrail.objects.create(
            activity=activity,
            changed_by=request.user if request.user.is_authenticated else None,
            field_changed="review_status",
            old_value=old_status,
            new_value="APPROVED & LOCKED"
        )

        return Response(
            {"message": f"Activity row successfully signed off and audit locked."}, 
            status=status.HTTP_200_OK
        )