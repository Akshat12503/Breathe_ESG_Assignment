import uuid
from django.db import models
from django.contrib.auth.models import User

class Tenant(models.Model):
    """Tracks individual enterprise clients using the platform to ensure data isolation."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return self.name

class TenantUser(models.Model):
    """Extends the default Django User to implement Role Based Access Control per tenant."""
    ROLE_CHOICES = [
        ('ANALYST', 'Sustainability Analyst'),
        ('AUDITOR', 'External Auditor'),
        ('ADMIN', 'Client Administrator'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tenant_profile')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ANALYST')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.role}) - {self.tenant.name}"

class IngestionSourceLog(models.Model):
    """Tracks every file upload or API sync batch for complete audit lineage."""
    SOURCE_CHOICES = [
        ('SAP_FUEL', 'SAP Procurement & Fuel Export'),
        ('UTILITY_ELECTRICITY', 'Utility Portal Electricity CSV'),
        ('CONCUR_TRAVEL', 'Corporate Travel Platform API'),
    ]
    STATUS_CHOICES = [
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='ingestion_logs')
    source_type = models.CharField(max_length=30, choices=SOURCE_CHOICES)
    filename_or_endpoint = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PROCESSING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.source_type} - {self.filename_or_endpoint} ({self.status})"

class NormalizedEmissionActivity(models.Model):
    """The central unified table holding standardized rows across Scopes 1, 2, and 3."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('SUSPICIOUS', 'Suspicious / Flagged'),
        ('APPROVED', 'Approved & Locked'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='activities')
    source_log = models.ForeignKey(IngestionSourceLog, on_delete=models.CASCADE, related_name='activities')
    
    # Core ESG Requirements
    scope_category = models.IntegerField(choices=[(1, 'Scope 1'), (2, 'Scope 2'), (3, 'Scope 3')])
    activity_type = models.CharField(max_length=100) # e.g., Diesel, Grid Electricity, Flight
    
    # Lineage and Staging Snapshot
    raw_data_snapshot = models.JSONField(help_text="Stores the original unparsed row payload for verification")
    raw_quantity = models.DecimalField(max_digits=15, decimal_places=4)
    raw_unit = models.CharField(max_length=50) # e.g., Liters, Gallons, kWh, Miles
    
    # Normalized Unified Fields
    normalized_quantity_kwh = models.DecimalField(max_digits=15, decimal_places=4, help_text="Energy normalized to kWh")
    co2e_emissions_mt = models.DecimalField(max_digits=15, decimal_places=4, help_text="Emissions in Metric Tonnes of CO2e")
    
    # Analyst Workflow Controls
    review_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    flag_reason = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"{self.activity_type} - {self.co2e_emissions_mt} MT CO2e ({self.review_status})"

class AuditTrail(models.Model):
    """Tracks historical manual adjustments made to any row by human analysts."""
    id = models.BigAutoField(primary_key=True)
    activity = models.ForeignKey(NormalizedEmissionActivity, on_delete=models.CASCADE, related_name='audit_history')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    field_changed = models.CharField(max_length=100)
    old_value = models.TextField()
    new_value = models.TextField()
    changed_at = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return f"Change on {self.field_changed} by {self.changed_by.username}"