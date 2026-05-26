# SOURCES.md: Source System Research & Real-World Mapping

[cite_start]This document provides the real-world operational context behind the simulated enterprise data pipelines implemented in the ingestion engine.

---

## 1. Source System Analysis

### [cite_start]Source 1: SAP MM Material Documents (Fuel Inventory) [cite: 24]
* [cite_start]**Real-World Interface Researched:** Material Management Inventory Ledger Movement Logs via SE16N standard reporting extractions[cite: 25].
* [cite_start]**Technical Parameters Discovered:** Standard SAP tracking keys use short German acronym parameters: `BUDAT` (Posting Date), `MATNR` (Material ID), `MENGE` (Quantity Payload), `MEINS` (Base Unit of Measure), and `WERK` (Plant Facility Identifier)[cite: 26].
* [cite_start]**Simulated Reality Handling:** Our seed records mock this exact behavior[cite: 21]. [cite_start]For example, a heavy stationary combustion row dumps an exact SAP string payload (`"BUDAT": "2026-03-01", "MATNR": "FUEL_OIL_09", "MENGE": "950000.00", "MEINS": "L"`)[cite: 21]. [cite_start]This line is explicitly caught by our anomaly rule and flagged as `SUSPICIOUS` because its volumetric flow exceeds the historical limits assigned to that specific plant ID (`PLNT_GER_11`)[cite: 17, 26].

### [cite_start]Source 2: Utility Portal Portal Extractions (Electricity) [cite: 28]
* [cite_start]**Real-World Interface Researched:** Regional Commercial Energy CSV Portal Exports (e.g., PG&E or ComEd Large Commercial Portals)[cite: 29].
* **Technical Parameters Discovered:** Large-scale commercial utility logs avoid simplified home metrics. [cite_start]They export high-resolution rows tracking Peak vs. Off-Peak usage, power factor efficiency losses, rolling demand metrics ($kW$), and pure energy generation volume consumption metrics ($kWh$)[cite: 30].
* **Simulated Reality Handling:** Our database handles a multi-month commercial invoice cycle. [cite_start]It reads a billing period spanning March to April, capturing original meter tracking values while converting peak demand indicators directly into baseline $kWh$ metrics[cite: 30].

### [cite_start]Source 3: Corporate Travel APIs (Scope 3 Business Flights) [cite: 31]
* [cite_start]**Real-World Interface Researched:** SAP Concur v4 Intelligence & Navan Analytics Webhooks[cite: 19, 32].
* [cite_start]**Technical Parameters Discovered:** Modern business travel platforms structure bookings by specific route segment dictionaries, mapping ticket class identifiers (`ECONOMY`, `BUSINESS`, `FIRST`) directly alongside distinct carbon classification tags[cite: 32, 33].
* [cite_start]**Simulated Reality Handling:** The script maps an international flight payload recording airport codes (`"segment": "JFK-FRA"`) and class metrics (`"cabin": "BUSINESS"`)[cite: 33]. [cite_start]The pipeline calculates emissions using cabin-specific emission coefficients, reflecting the fact that business class seats take up more physical space on an aircraft and carry a higher carbon footprint share under the GHG Protocol[cite: 32].

---

## 2. What Would Break in a Real Production Deployment

[cite_start]Moving from a prototype environment to a production data architecture exposes three critical real-world failure points:

1. **Unregistered Custom Units of Measure:** In production, an asset manager might manually input a fuel invoice using an unmapped local unit abbreviation (e.g., `BBL` for barrels or `bsh` for bushels). [cite_start]Without a dynamic unit fallback service, the serialization layer will crash[cite: 26].
2. **CORS and Host Header Restrictions with External Webhooks:** While our local setup relies on permissive CORS settings (`CORS_ALLOW_ALL_ORIGINS = True`), a production cloud environment will block external API callbacks unless your reverse proxy (like Nginx) is explicitly configured to handle the specific incoming host domains securely.
3. **Database Locks and Connection Timeouts During Large Imports:** Processing massive, multi-megabyte CSV uploads directly inside a standard web request loop will trigger connection timeouts. Production environments must offload file processing to an asynchronous worker queue (such as Celery using a Redis broker) to keep the web application highly responsive.