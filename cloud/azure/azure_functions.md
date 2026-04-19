# Azure Functions

## 1) What is the Service?
Azure Functions is a serverless compute service to run event-driven code without managing servers.

## 2) When to Use?
- Lightweight transformations
- API/webhook handlers
- Event routing, validation, enrichment
- Scheduled housekeeping jobs

## 3) Architecture Usage
`Event Hubs/Blob Trigger → Azure Function → ADLS/Synapse/Cosmos`

## 4) Real-World Example
Uber-like event validation:
- Validate ride events
- Enrich with city metadata
- Route valid events to streaming pipeline

## 5) Integration with Other Services
- Event Hubs triggers
- Blob triggers with ADLS
- HTTP triggers from Logic Apps/APIM
- Output bindings to Cosmos DB, Queue, Service Bus

## 6) Common Mistakes
- Long-running heavy ETL inside Functions
- Ignoring cold starts
- No retry/dead-letter strategy

## 7) Performance Tips
- Keep handlers small and stateless
- Use premium plan for low-latency needs
- Batch writes where possible
- Reuse connections across invocations

## 8) 🔥 Interview Questions
1. Functions vs Lambda vs Cloud Functions?
2. How to handle retries and poison messages?
3. When should Function call Databricks instead of transforming directly?
