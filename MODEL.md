# Data Model Blueprint

## 1. Core Architecture Design
To handle multi-tenancy and high data integrity, this system utilizes a **Unified Normalization Layer**. Raw incoming rows from disparate sources (SAP, Utility, Concur) are parsed, validated, and transformed into a standardized, audit-ready ledger.

## 2. Model Schema (Django ORM Entities)

### Tenant
Tracks individual enterprise clients using the platform to ensure data isolation.
* `id`: UUID (Primary Key)
* `name`: CharField (Company Name)
* `created_at`: DateTimeField

### User (Role Based Access Control)
* `id`: UUID (Primary Key)
* `tenant`: ForeignKey(Tenant)
* `role`: CharField (Choices: 'ANALYST', 'AUDITOR', 'ADMIN')

### IngestionSourceLog (Source-of-Truth & Lineage)
Tracks every file upload or API sync batch.
* `id`: UUID (Primary Key)
* `tenant`: ForeignKey(Tenant)
* `source_type`: CharField (Choices: 'SAP_PRICING_FUEL', 'UTILITY_CSV', 'CONCUR_TRAVEL_API')
* `filename_or_endpoint`: CharField
* `uploaded_by`: ForeignKey(User)
* `status`: CharField ('PROCESSING', 'COMPLETED', 'FAILED')
* `created_at`: DateTimeField

### NormalizedEmissionActivity (The Central Ledger)
The ultimate table holding unified, cleaned rows across all scopes.
* `id`: UUID (Primary Key)
* `tenant`: ForeignKey(Tenant)
* `source_log`: ForeignKey(IngestionSourceLog)
* `scope_category`: IntegerField (Choices: 1, 2, 3) 
* `activity_type`: CharField (e.g., "Diesel Fuel Purchase", "Grid Electricity", "Air Travel")
* `raw_data_snapshot`: JSONField (Stores the original unparsed row for audit verification)
* `raw_quantity`: DecimalField
* `raw_unit`: CharField (e.g., "Liters", "kWh", "Miles")
* `normalized_quantity_kwh`: DecimalField (All energy consumption normalized to kWh for baseline conversion)
* `co2e_emissions_mt`: DecimalField (Calculated Metric Tonnes of CO2 equivalent)
* `review_status`: CharField (Choices: 'PENDING', 'SUSPICIOUS', 'APPROVED')
* `flag_reason`: TextField (Null if status is clear; explains suspicious markers)
* `reviewed_by`: ForeignKey(User, null=True)
* `reviewed_at`: DateTimeField (null=True)

### AuditTrail (Data Versioning)
Tracks any human corrections made to rows post-ingestion.
* `id`: AutoField
* `activity`: ForeignKey(NormalizedEmissionActivity)
* `changed_by`: ForeignKey(User)
* `field_changed`: CharField
* `old_value`: TextField
* `new_value`: TextField
* `changed_at`: DateTimeField