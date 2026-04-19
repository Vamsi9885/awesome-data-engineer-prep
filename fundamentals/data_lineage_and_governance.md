# 🕸️ Data Lineage & Governance

## 1. Concept Explanation

**Lineage = Data Family Tree**
```
Table sales → FROM orders × products
→ WHO changed? WHEN? WHY?

Governance: Who can access? Compliance?
```

**Why Critical:**
```
Audit: PCI-DSS requires lineage
Debug: Broken pipeline → Trace source
Compliance: GDPR data deletion
Impact Analysis: Drop column safely?
```

**Tools:**
| Tool | Lineage | Governance | Cost |
|------|---------|------------|------|
| Collibra | ✅ | ✅ Enterprise | $$$$ |
| DataHub | ✅ | ✅ Open-source | $ |
| Atlas | ✅ Hive | ❌ | Free |
| Amundsen | ✅ Catalog | ❌ | Free |

## 2. Real-World Example - Amazon

```
1PB data → DataHub tracks lineage
Query: "sales_golden" lineage → 15 upstream tables
Delete PII: Trace + delete across 50 tables
```

## 3. Practical Scenario

**Uber Finance Audit:**
```
Regulator: "Show order_total calculation"
Lineage: orders → raw_events × exchange_rates
→ 5min vs 5 days manual tracing
```

## 4. Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| No lineage | Audit fails | Auto-capture (DataHub) |
| Manual tags | Scale impossible | Automated classification |
| No access control | Data leaks | RBAC + column masking |
| Siloed metadata | Duplicate effort | Centralized catalog |

## 5. Performance Tips

```
🏆 Governance Tier List:
S-Tier: DataHub + Unity Catalog
A-Tier: Collibra
B-Tier: Custom Apache Atlas

Query +1s lineage lookup
```

**DataHub Integration:**
```
Spark → DataHub lineage capture
dbt → Lineage diagrams auto-generated
```

## 6. 🔥 Interview Questions

### Amazon L5
**Q1: Why data lineage critical in enterprises?**
```
A: 1. Compliance (GDPR/SOX) 2. Debug pipelines
   3. Impact analysis 4. Cost attribution
```

**Q2 Follow-up: Implement lineage at scale?**
```
A: OpenLineage standard + DataHub
   Spark/dbt/airflow integrations
```

### Uber L4
**Q3: GDPR PII deletion across 100 tables?**
```
A: Lineage traversal + automated deletion
   Column tagging + propagation
```

**Q4: Data catalog vs lineage?**
```
A: Catalog: WHERE data is
   Lineage: HOW data flows
```

### Netflix Scenario
**Q5: Broken dashboard. Find root cause fast?**
```
A: Lineage graph → Trace upstream
   Column-level lineage critical
```

**Q6: Governance for 1000 engineers?**
```
A: Self-service catalog + RBAC
   Automated tagging + approval workflows
```

---

**⚡ Pro Tip:** No lineage = Blind data operations.
