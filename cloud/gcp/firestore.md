# Google Firestore

## 1) What is the Service?
Firestore is a managed document database optimized for application-centric data models and real-time sync patterns.

## 2) When to Use?
- App metadata/state for web/mobile backends
- Lightweight operational stores in event pipelines
- Document-centric access patterns

## 3) Architecture Usage
`Apps/Functions → Firestore operational data → periodic export to BigQuery/GCS for analytics`

## 4) Real-World Example
Consumer app preferences:
- User personalization settings stored in Firestore
- Daily export joined with behavioral data for recommendation tuning

## 5) Integration with Other Services
- Cloud Functions triggers
- Pub/Sub bridge patterns
- BigQuery export for analytics

## 6) Common Mistakes
- Modeling for relational joins
- Deep nested documents with heavy update patterns
- No indexes for query-heavy fields

## 7) Performance Tips
- Design collections by access path
- Use composite indexes where needed
- Avoid large hot documents
- Control document size and update frequency

## 8) 🔥 Interview Questions
1. Firestore vs Bigtable vs BigQuery?
2. Firestore vs DynamoDB/Cosmos DB in data platforms?
3. How to move operational docs into analytics pipelines?
