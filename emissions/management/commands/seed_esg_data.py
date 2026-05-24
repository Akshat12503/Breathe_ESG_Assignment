import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from emissions.models import Tenant, TenantUser, IngestionSourceLog, NormalizedEmissionActivity

class Command(BaseCommand):
    help = "Seeds the database with highly realistic enterprise ESG data streams."

    def handle(self, *args, **options):
        self.stdout.write("Starting ESG data seeding...")

        # 1. Establish the Tenant Client
        tenant, created = Tenant.objects.get_or_create(name="Apex Enterprise Solutions")
        
        # 2. Establish the Analyst Workspace Account
        auth_user, u_created = User.objects.get_or_create(username="analyst_user")
        if u_created:
            auth_user.set_password("esgpass123")
            auth_user.save()
        
        tenant_user, tu_created = TenantUser.objects.get_or_create(
            user=auth_user,
            tenant=tenant,
            role="ANALYST"
        )

        # Clear existing entries for idempotent clean runs
        NormalizedEmissionActivity.objects.filter(tenant=tenant).delete()
        IngestionSourceLog.objects.filter(tenant=tenant).delete()

        # ==========================================
        # STREAM 1: SAP PROCUREMENT EXPORT (Scope 1)
        # ==========================================
        sap_log = IngestionSourceLog.objects.create(
            tenant=tenant,
            source_type="SAP_FUEL",
            filename_or_endpoint="SAP_MM_MATDOC_2026_Q1.csv",
            uploaded_by=auth_user,
            status="COMPLETED"
        )

        # Normal row
        NormalizedEmissionActivity.objects.create(
            tenant=tenant,
            source_log=sap_log,
            scope_category=1,
            activity_type="Stationary Combustion - Diesel",
            raw_data_snapshot={
                "BUDAT": "2026-02-15",
                "MATNR": "DIESEL_004",
                "MENGE": "5000.00",
                "MEINS": "L",
                "WERK": "PLNT_IND_40"
            },
            raw_quantity=Decimal("5000.00"),
            raw_unit="Liters",
            normalized_quantity_kwh=Decimal("5000.00") * Decimal("10.0"),  # Approx 10 kWh/L
            co2e_emissions_mt=Decimal("13.4000"), # Calculated using standard diesel conversion factor
            review_status="PENDING"
        )

        # Suspicious row: Extreme purchasing volume anomaly
        NormalizedEmissionActivity.objects.create(
            tenant=tenant,
            source_log=sap_log,
            scope_category=1,
            activity_type="Stationary Combustion - Fuel Oil",
            raw_data_snapshot={
                "BUDAT": "2026-03-01",
                "MATNR": "FUEL_OIL_09",
                "MENGE": "950000.00", # Massive outlier
                "MEINS": "L",
                "WERK": "PLNT_GER_11"
            },
            raw_quantity=Decimal("950000.00"),
            raw_unit="Liters",
            normalized_quantity_kwh=Decimal("950000.00") * Decimal("10.5"),
            co2e_emissions_mt=Decimal("2540.5000"),
            review_status="SUSPICIOUS",
            flag_reason="Outlier Alert: Volume exceeds historical baseline for Plant GER_11 by 450%."
        )

        # ==========================================
        # STREAM 2: UTILITY PORTAL EXPORT (Scope 2)
        # ==========================================
        utility_log = IngestionSourceLog.objects.create(
            tenant=tenant,
            source_type="UTILITY_ELECTRICITY",
            filename_or_endpoint="Facility_Grid_Bill_Midwest_Mar.csv",
            uploaded_by=auth_user,
            status="COMPLETED"
        )

        # Realistic non-calendar billing cycle: March 12 to April 11
        NormalizedEmissionActivity.objects.create(
            tenant=tenant,
            source_log=utility_log,
            scope_category=2,
            activity_type="Purchased Electricity - Grid",
            raw_data_snapshot={
                "Account_Number": "ACC-88392-1",
                "Service_Start": "2026-03-12",
                "Service_End": "2026-04-11",
                "Usage_kwh": "42500.00",
                "Tariff_Code": "E-IND-MIDWEST"
            },
            raw_quantity=Decimal("42500.00"),
            raw_unit="kWh",
            normalized_quantity_kwh=Decimal("42500.00"),
            co2e_emissions_mt=Decimal("16.8500"), # regional grid factor applied
            review_status="PENDING"
        )

        # ==========================================
        # STREAM 3: PLATFORM API FLIGHTS (Scope 3)
        # ==========================================
        travel_log = IngestionSourceLog.objects.create(
            tenant=tenant,
            source_type="CONCUR_TRAVEL",
            filename_or_endpoint="https://api.concur.com/v4/travel/bookings",
            uploaded_by=auth_user,
            status="COMPLETED"
        )

        # Airport code resolving scenario
        NormalizedEmissionActivity.objects.create(
            tenant=tenant,
            source_log=travel_log,
            scope_category=3,
            activity_type="Business Travel - Air",
            raw_data_snapshot={
                "booking_id": "CNCR-99201A",
                "origin_airport": "DEL",
                "destination_airport": "BOM",
                "cabin_class": "Business",
                "pax_count": 1
            },
            raw_quantity=Decimal("1140.00"), # Distance in kilometers resolved via internal lookup
            raw_unit="Kilometers",
            normalized_quantity_kwh=Decimal("0.00"), # Air travel doesn't directly consume tenant facility grid energy
            co2e_emissions_mt=Decimal("0.2400"), # Higher flight emission coefficient applied due to business class weighting
            review_status="PENDING"
        )

        self.stdout.write(self.style.SUCCESS("Successfully seeded 4 highly detailed corporate sustainability activities!"))