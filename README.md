# Breathe ESG - Data Normalization & Pre-Audit Verification Workspace

An enterprise-grade ESG (Environmental, Social, and Governance) data pipelines platform designed to ingest raw activity logs from disparate corporate systems, normalize values into unified reporting metrics (kWh and MT CO₂e), flag data anomalies, and provide an analytical workflow for pre-audit verification.

## 🚀 Key Architectural Strengths
* **Strict Data Isolation (Multi-Tenancy):** Built with explicit tenant scoping (`Tenant` and `TenantUser` models) to safeguard data isolation across separate corporate entities.
* **Raw Data Lineage Snapshotting:** Preserves an exact, immutable JSON payload of the raw source system record (`raw_data_snapshot`) to ensure complete reproducibility and a clean data lineage from the source system to the final footprint.
* **Immutable Audit Trail Ledger:** Employs an append-only transaction ledger (`AuditTrail`) that records a historic snapshot (old state, new state, user ID, timestamp) whenever an analytical override occurs.
* **Idempotent Pipeline Infrastructure:** Ingestion commands leverage strict checksum unique constraints to prevent duplicate line-item parsing during system retries.

---

## 🛠️ Technology Stack Translation Mapping

This platform leverages modern full-stack development patterns. Coming from a .NET & Angular background, the system maps directly to familiar enterprise structures:

### Backend Architecture (Django REST Framework vs. .NET)
* **Data Layer / ORM:** Implemented via Django Models (`models.py`), operating identically to **Entity Framework Core (EF Core)** code-first modeling.
* **Data Transfer Objects (DTO):** Managed via `serializers.py` to securely sanitize and format database structures into public-facing JSON schemas, operating exactly like **AutoMapper** profile models.
* **Controllers & Endpoints:** Handled via DRF ViewSets (`views.py`) utilizing action routing to expose GET listings and custom POST transaction states, functioning identically to **Web API Controllers**.

### Frontend Interface (React vs. Angular)
* **State Management:** Uses the declarative functional state hook (`useState`), replacing imperative component class properties and Angular's change-detection loops.
* **Lifecycle Gateway:** Employs `useEffect` to dispatch asymmetric cross-origin network fetches upon component mounting, mapping directly to `ngOnInit()` pipeline hooks.

---

## 📋 Pre-Audit Edge Cases Successfully Solved
The ingestion pipeline handles 4 complex corporate scenarios out of the box:
1. **Stationary Combustion (Scope 1 - Diesel):** Parses legacy ERP formatting containing localized metrics (Liters) into baseline metrics.
2. **Stationary Combustion (Scope 1 - Fuel Oil Anomaly):** Successfully flags massive purchase transactions deviating from plant historical baselines by 450% as `SUSPICIOUS`.
3. **Purchased Electricity (Scope 2 - Grid Bill):** Tracks overlapping invoice timelines (March–April utility invoicing cycles).
4. **Business Travel (Scope 3 - Flights):** Dynamically processes airport string pairs (e.g., `JFK-FRA`) to assess Scope 3 flight leg values.

---

## 💻 Local Setup & Execution Guide

Follow these steps to run both the Django backend and React frontend services simultaneously on a local workspace machine:

### Prerequisites
* Python 3.12+
* Node.js (v18 or higher)
* npm (v10 or higher)

### 1. Initialize and Run the Backend Server
Open a terminal in the root directory and run:
```powershell
# Activate the Python virtual environment
.\venv\Scripts\Activate.ps1

# Run database migrations
python manage.py migrate

# Boot up the backend API server
python manage.py runserver