# Azure Logic Apps

## 1) What is the Service?
Logic Apps is Azure’s low-code workflow automation service for integrating systems, APIs, and enterprise processes.

## 2) When to Use?
- Event-driven enterprise integration
- Notifications, approvals, and data movement glue logic
- SaaS connectors without custom code

## 3) Architecture Usage
`ADF/Synapse completion event → Logic Apps → approvals/alerts/ticketing`

## 4) Real-World Example
Retail data SLA ops:
- If nightly pipeline fails, Logic Apps opens incident and notifies on-call teams
- On success, sends business readiness signal to reporting stakeholders

## 5) Integration with Other Services
- ADF, Synapse, Event Grid
- Teams/Outlook/ServiceNow connectors
- Azure Functions for custom logic

## 6) Common Mistakes
- Using Logic Apps for heavy data processing
- Complex logic without modularization
- Missing retry/timeout handling

## 7) Performance Tips
- Keep flows composable and idempotent
- Use asynchronous patterns for external APIs
- Apply proper trigger filters to reduce noise

## 8) 🔥 Interview Questions
1. Logic Apps vs Step Functions?
2. Where should orchestration end and business workflow begin?
3. How to build reliable alerting for failed ETL SLAs?
