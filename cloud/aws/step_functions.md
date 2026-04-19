# AWS Step Functions

## 1) What is the Service?
Step Functions is a serverless workflow orchestration service for coordinating distributed tasks and state transitions.

## 2) When to Use?
- Multi-step pipelines with retries/branches
- Coordinating Lambda, Glue, EMR, ECS, API calls
- Long-running business workflows with visibility

## 3) Architecture Usage
`EventBridge trigger → Step Functions DAG → Glue/EMR/Lambda → S3/Redshift`

## 4) Real-World Example
Marketplace daily pipeline:
- Validate source arrival
- Run Glue jobs in sequence
- Branch on quality checks
- Notify Slack/Email on failure paths

## 5) Integration with Other Services
- Lambda, Glue, EMR, Batch, ECS, SNS/SQS
- CloudWatch/X-Ray for monitoring

## 6) Common Mistakes
- Putting heavy compute in state machine instead of compute services
- No idempotent task design
- Poor error path definitions

## 7) Performance Tips
- Keep states focused and composable
- Use parallel states for independent branches
- Centralize retries and catch handlers
- Use Express workflows for high-volume short workflows

## 8) 🔥 Interview Questions
1. Step Functions vs Airflow?
2. How do you design retry/backoff in complex pipelines?
3. How to guarantee exactly-once effects with at-least-once tasks?
