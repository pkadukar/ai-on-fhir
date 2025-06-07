
# Security & Compliance Plan
This document outlines the current and future plans for ensuring HIPAA-aligned security and compliance in the AI-on-FHIR query tool.

## Authentication & Authorization
- The system uses **JWT (JSON Web Tokens)** for authentication.
- All protected routes (e.g., `/query`) require a valid token obtained via `/login`.
- This ensures only registered users can access patient-query endpoints.

## Future Integration: SMART on FHIR & OAuth 2.0
- For full HIPAA-aligned systems, consider implementing **SMART on FHIR** using OAuth 2.0 authorization.
- This would allow secure user-specific access tied to EHR systems.

## Data Privacy & Transport Security
- All communication should occur over **HTTPS** in production.
- Query results do not include sensitive PII—only simulated structured data (conditions, age, etc.).
- No actual patient identifiers are stored or returned.

## Audit Logging Strategy (Planned)
- Future logging can include:
  - Timestamp of each query
  - JWT identity (username)
  - Query string
- Logs can be stored securely to monitor usage and detect misuse.

## Role-Based Access Control (RBAC)
- Future implementation could define roles:
  - `admin`: full access to logs, all queries
  - `clinician`: access to patient queries only
  - `viewer`: read-only, filtered query access
- This would enforce principle of least privilege.
