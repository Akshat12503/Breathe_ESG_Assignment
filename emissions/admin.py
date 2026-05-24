from django.contrib import admin
from .models import Tenant, TenantUser, IngestionSourceLog, NormalizedEmissionActivity, AuditTrail

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')

@admin.register(TenantUser)
class TenantUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant', 'role')
    list_filter = ('role', 'tenant')

@admin.register(IngestionSourceLog)
class IngestionSourceLogAdmin(admin.ModelAdmin):
    list_display = ('source_type', 'filename_or_endpoint', 'tenant', 'status', 'created_at')
    list_filter = ('source_type', 'status', 'tenant')

@admin.register(NormalizedEmissionActivity)
class NormalizedEmissionActivityAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'scope_category', 'tenant', 'co2e_emissions_mt', 'review_status')
    list_filter = ('review_status', 'scope_category', 'tenant')
    search_fields = ('activity_type', 'flag_reason')

@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('activity', 'field_changed', 'old_value', 'new_value', 'changed_by', 'changed_at')