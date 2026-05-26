# DECISIONS.md: Ambiguity Resolutions and Strategic Engineering Assumptions

[cite_start]During a rapid 4-day prototype timeline, raw business requirements always present systemic engineering ambiguities[cite: 9]. [cite_start]This document clarifies the constraints handled by the system and lists the technical questions compiled for the Product Management organization.

---

## 1. Ambiguities Resolved & Selected Scope Boundaries

### A. SAP Integration Scope (Direct Fuel Inventory Sub-Module)
* [cite_start]**The Ambiguity:** SAP data exports can arrive as complex asynchronous IDocs, OData web streams, or manual table extractions[cite: 25].
* [cite_start]**The Resolution:** We scoped the intake process to model **Material Management (SAP MM) Material Document Logs (Table MSEG / Transaction MB51)** extracted via flat CSV[cite: 24, 25]. We intentionally ignored financial ledger accounting records (SAP FI) and manufacturing lifecycle tracking (SAP PP) to lock focus on verifiable material inventory movements.
* [cite_start]**What was Ignored:** Plant codes (e.g., `PLNT_GER_11`) are treated as literal text values[cite: 26]. The prototype skips building out a full warehouse dictionary lookup database to keep the data mapping clean and fast.

### B. Utility Data Invoicing Overlaps
* [cite_start]**The Ambiguity:** Utility bills follow regional meter-reading timelines that rarely match strict calendar months, meaning a single billing period can easily span multiple quarters[cite: 30].
* [cite_start]**The Resolution:** The database records invoices by their actual calendar-agnostic date spans[cite: 30]. When aggregating totals for a carbon disclosure report, our calculation engine divides the total emissions proportionally by the exact number of days overlapping that month. For example, if a bill covers 30 days in March and 15 days in April, two-thirds of its carbon footprint is allocated to Q1, and one-third is allocated to Q2.

### C. Corporate Travel Location Parsing
* [cite_start]**The Ambiguity:** Corporate travel applications like Concur often export airport code pairs (e.g., `JFK-FRA`) instead of calculating literal travel distances[cite: 33].
* **The Resolution:** Our pipeline treats destination strings as a direct foreign key for emission calculations. The intake script implements an algorithmic lookup that checks standard Great Circle distance metrics between international hub airport pairs to convert airport coordinates directly into $MT CO_2e$ figures.

---

## 2. Technical Questions for the Product Manager (PM)

[cite_start]If this project were moving from a prototype to a production sprint cycle, these are the critical requirements clarifications required from the PM:

1. **Analytical Audit Workflow Roles:** When an analyst triggers an "Approve & Lock" transaction, should the system enforce a multi-step verification process? Do we need to separate permissions between Level 1 Analysts (who flag rows) and Level 2 Sustainability Directors (who sign off on locked audit records)?
2. **Flag Modification Rights:** Can an analyst manually modify raw ingestion quantities if they spot a clerical typo inside a source utility CSV, or should they be forced to reject the row entirely and request a clean source file upload to preserve total data lineage integrity?
3. **Multi-Currency Standardization:** SAP procurement logs frequently mix currencies across operating locations (e.g., EUR, USD, INR). Should the platform consume currency conversion values dynamically via an active external financial exchange API, or will the client supply static currency exchange baseline tables for each fiscal reporting period?