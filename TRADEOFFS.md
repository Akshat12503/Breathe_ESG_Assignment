# TRADEOFFS.md: Strategic Engineering Scope Postponements

[cite_start]To deliver a highly stable, production-grade MVP within a strict 4-day deadline, features were prioritized by their architectural value[cite: 9, 14]. [cite_start]This document defines three elements that were deliberately excluded from the system and justifies why those boundaries were drawn.

---

## 1. Deliberate Omission: Dynamic PDF Parsing Layer (OCR Ingestion)

* [cite_start]**What was postponed:** Building an automated ingestion engine that lets users upload raw utility bills as PDF files, extracting data using Optical Character Recognition (OCR) or Large Language Models[cite: 29, 34].
* **Technical Justification:** Building a production-ready OCR pipeline requires complex document layout parsing, confidence scoring, and intensive background processing loops. [cite_start]Attempting to cram a rough, un-optimized OCR model into an MVP inevitably results in unstable data extractions and frequent pipeline errors. [cite_start]Instead, I restricted the ingestion boundaries to structured CSV portal exports[cite: 29, 43]. [cite_start]This locks focus onto the data normalization schema, calculation precision, and human sign-off interfaces, which are the most critical pillars of an auditable system[cite: 17, 39].

---

## 2. Deliberate Omission: Fully Flexible Database-Driven Emissions Factor Engine

* **What was postponed:** Designing a fully dynamic dashboard interface that lets admins add, edit, and version custom greenhouse gas emission conversion factors across international regulatory regions.
* **Technical Justification:** Real-world carbon accounting relies on massive, constantly shifting regulatory databases (like EPA, DEFRA, or IEA tables). Designing a highly scalable relational database schema just to handle the edge-case versioning of those conversion factors would dramatically overcomplicate the core data model. For this prototype, emission factor transformations are managed through structured, code-based lookup tables on the backend. [cite_start]This architecture provides the evaluator with crystal-clear visibility into how the calculations work under the hood without introducing unnecessary schema complexity[cite: 14].

---

## 3. Deliberate Omission: Row-Level RBAC and Active JWT Authentication

* **What was postponed:** Implementing strict Role-Based Access Control (RBAC) across the React dashboard to lock individual rows down by regional analyst teams, backed by active JSON Web Token (JWT) authorization headers.
* [cite_start]**Technical Justification:** While the database model is fully structured for security using tenant-isolation boundaries [cite: 39][cite_start], implementing a complete production-grade authentication framework within a short prototyping phase often introduces configuration bugs that can completely block an evaluator from reviewing your live application[cite: 47]. Instead, the workspace uses a single unified analyst interface paired with standard Django session authentication for the admin views. [cite_start]This approach keeps the cross-origin API pipeline completely bulletproof while keeping the reviewer's access experience entirely friction-free[cite: 56].