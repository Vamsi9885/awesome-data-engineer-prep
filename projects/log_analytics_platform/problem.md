# Log Analytics Platform — Problem Statement

## Business Context
A SaaS company runs hundreds of microservices across regions. Engineering, security, and product teams need near-real-time observability for:
- incident triage
- SLA tracking
- anomaly detection
- security audits

Current logs are siloed per service with inconsistent formats, making cross-service analysis slow and unreliable.

## Functional Requirements
- Ingest logs from apps, API gateways, infra agents, and audit systems.
- Support structured and semi-structured logs (JSON/text).
- Parse, normalize, enrich (service, env, region, trace IDs).
- Deduplicate repeated log entries.
- Handle late-arriving and out-of-order logs.
- Build curated datasets for:
  - error trends
  - latency percentiles
  - security events
  - request tracing
- Expose search-ready and analytics-ready layers.
- Support retention + archival with tiered storage.

## Non-Functional Requirements
- Ingestion scale: 5 TB/day logs.
- P95 ingestion-to-query latency < 2 minutes.
- 99.95% availability for search dashboards.
- Idempotent replay and exactly-once analytics outputs.
- Cost controls for storage and compute growth.
- Regulatory retention and audit readiness.

## Data Challenges
- Schema drift from rapid service releases.
- Key skew from hot services/endpoints.
- Duplicate log shipping during agent retries.
- Bursty traffic during incidents.
- High-cardinality fields (user IDs, session IDs).

## Success Metrics
- MTTR reduced by 40%.
- Query success > 99.9%.
- Alert precision improved (false positives reduced by 25%).
- Cost/GB indexed within budget target.
