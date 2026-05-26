# MODEL.md: Architectural Data Model Specification

This document details the schema design choices implemented in the PostgreSQL/SQLite relational database for the Breathe ESG platform. The data model prioritizes relational integrity, strict logical data isolation, immutable audit ledgers, and clear tracking of raw data lineage.

---

## 1. Entity Relationship Overview & Relational Strategy

The architecture separates concerns into three distinct layers:
1. [cite_start]**Identity & Access Management Layer:** `Tenant` and `TenantUser` tables ensure logical boundaries.
2. [cite_start]**Ingestion & Processing Layer:** `IngestionSourceLog` tracks data provenance (lineage) before manipulation.
3. [cite_start]**Normalized Ledger Layer:** `NormalizedEmissionActivity` stores post-calculation metrics, while `AuditTrail` records state changes.

---

## 2. Model Schemas & Field Justifications

### A. Tenant Scoping (`Tenant`)
To support true corporate multi-tenancy, every operational row must roll up to a root tenant instance. This completely avoids accidental cross-contamination of client data.
* `id` (UUIDv4, Primary Key): Guarantees globally unique identifiers across potential distributed database nodes.
* `name` (VARCHAR): The official corporate name of the registered entity (e.g., "Apex Enterprise Solutions").

### B. Ingestion Logging (`IngestionSourceLog`)
This model maps data provenance (source-of-truth tracking). It records exactly which data provider generated a pipeline run, when it executed, and what the baseline document was named.
* `id` (UUIDv4, Primary Key)
* `tenant` (ForeignKey -> Tenant): Enforces tenant boundary isolation.
* `source_type` (VARCHAR): Restructured choices matching the three operational channels: `SAP_FUEL`, `UTILITY_ELECTRICITY`, or `CORPORATE_TRAVEL`[cite: 24, 28, 31].
* `filename_or_endpoint` (VARCHAR): Captures the specific source marker (e.g., `SAP_MM_MATDOC_2026_Q1.csv` or a specific API request hash)[cite: 25, 29, 34].

### C. Normalized Emission Analytics (`NormalizedEmissionActivity`)
The primary target engine model. It captures raw inputs , standardizes conversion values to unified figures , categorizes rows into GHG protocol scopes , and registers verification states[cite: 17].
* `id` (UUIDv4, Primary Key)
* `source_log` (ForeignKey -> IngestionSourceLog): Connects the calculated output to its exact raw source lineage file.
* `scope_category` (INTEGER): Direct map matching GHG Protocol metrics: `1` (Direct), `2` (Indirect Market/Grid), or `3` (Value Chain).
* `activity_type` (VARCHAR): Human-readable sub-category description (e.g., "Stationary Combustion - Fuel Oil").
* `raw_data_snapshot` (JSONB): **Critical Lineage Choice.** Stores the exact immutable row slice extracted from the source system prior to math application. This ensures that if emissions factor logic shifts in the future, the baseline record remains fully reproducible and completely auditable.
* `raw_quantity` & `raw_unit` (DECIMAL / VARCHAR): Preserves original file parameters (e.g., `950,000` and `Liters`).
* `normalized_quantity_kwh` (DECIMAL): Normalizes all varying volume and mass figures into standard thermodynamic energy equivalents for uniform storage.
* `co2e_emissions_mt` (DECIMAL): The ultimate calculated footprint quantified in Metric Tons of Carbon Dioxide Equivalent ($MT CO_2e$).
* `review_status` (VARCHAR): Workflow state constraints: `PENDING`, `SUSPICIOUS` (Anomalous payload), or `APPROVED & LOCKED`[cite: 17].
* `flag_reason` (TEXT): Nullable string registering pipeline automation explanations for anomalies (e.g., "Outlier Alert: Volume exceeds historical baseline by 450%").

### D. System Ledger Audit Tracking (`AuditTrail`)
An append-only transaction table storing analytical override mutations.
* `id` (UUIDv4, Primary Key)
* `activity` (ForeignKey -> NormalizedEmissionActivity): The target database row under evaluation.
* `field_changed` (VARCHAR): Name of the modified database element (typically `review_status`).
* `old_value` / `new_value` (TEXT): Tracks data mutations from `PENDING` or `SUSPICIOUS` into locked compliance metrics[cite: 17, 39].
* `changed_at` (TIMESTAMP): Set automatically to tracking runtime clock.

---

## 3. Defense of Architectural Decisions

### Why JSONB for Raw Snapshots?
Instead of creating a messy web of relational column fields matching every custom legacy column found across foreign tools, we dump raw unstructured line data into a highly indexed PostgreSQL `JSONB` or standard text field. This guarantees that no legacy transaction parameters are dropped during ingestion, giving external auditors immediate line-of-sight validation inside the final target UI dashboard.

### Why Multi-Tenancy at the Table Level?
By enforcing a strict `tenant_id` foreign key check across all operational records, data queries can easily implement global filter wrappers. In a production .NET ecosystem, this mirrors configuring Entity Framework Global Query Filters, ensuring that even if a developer omits a `Where()` clause in a future view API, tenant row leakages are mathematically impossible.
