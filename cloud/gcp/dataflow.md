# Google Cloud Dataflow

## 1) What is the Service?
Dataflow is GCP’s managed execution service for Apache Beam pipelines (batch + streaming).

## 2) When to Use?
- Unified batch and stream processing
- Complex event-time/windowing logic
- Low-ops autoscaling stream jobs

## 3) Architecture Usage
`Pub/Sub → Dataflow (Beam transforms) → BigQuery/GCS/Bigtable`

## 4) Real-World Example
Streaming ETA analytics:
- Ride events from Pub/Sub
- Dataflow computes rolling city congestion and ETA features
- Results land in BigQuery every few seconds

## 5) Integration with Other Services
- Pub/Sub sources
- BigQuery sinks
- GCS staging/checkpoints
- Composer orchestration for batch templates

## 6) Common Mistakes
- Incorrect watermark/window strategy
- Ignoring dead-letter paths for bad records
- Overly stateful transforms without memory planning

## 7) Performance Tips
- Use autoscaling and Streaming Engine
- Design efficient keys to reduce hot-key pressure
- Minimize serialization overhead
- Separate heavy enrichment into side inputs or external stores carefully

## 8) 🔥 Interview Questions
1. Dataflow vs Spark Structured Streaming?
2. What are watermarks/triggers and why critical?
3. How to debug lag in high-throughput Dataflow jobs?
