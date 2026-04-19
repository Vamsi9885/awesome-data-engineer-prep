# Azure Stream Analytics (ASA)

## 1) What is the Service?
Azure Stream Analytics is a managed real-time stream processing engine using SQL-like query language.

## 2) When to Use?
- Lightweight real-time aggregations and filtering
- Fast stream-to-dashboard use cases
- Low-ops alternative to custom streaming code

## 3) Architecture Usage
`Event Hubs/IoT Hub → ASA queries → Synapse/Power BI/ADLS`

## 4) Real-World Example
Logistics operations:
- Compute near-real-time delayed shipment counts by region
- Push rolling metrics directly to dashboard sinks

## 5) Integration with Other Services
- Event Hubs inputs
- ADLS and Synapse outputs
- Power BI real-time dashboards
- Functions for custom extensions

## 6) Common Mistakes
- Using ASA for complex stateful logic better suited for Spark/Flink
- No late-event handling strategy
- Poorly designed windows leading to noisy results

## 7) Performance Tips
- Use proper tumbling/hopping/sliding windows
- Keep queries simple and composable
- Partition input streams for parallel processing
- Monitor watermark delays and output latency

## 8) 🔥 Interview Questions
1. ASA vs Databricks Structured Streaming?
2. Event Hubs + ASA vs Kinesis + Lambda patterns?
3. How do windowing and late arrivals affect correctness?
