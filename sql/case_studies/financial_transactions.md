# 🧪 CASE STUDY - Financial Transactions (Banking/Payments)

## Scenario
Build fraud/risk and reconciliation analytics on payments table.

## Sample Data
| txn_id | account_id | txn_time             | txn_type | amount | status   |
|------:|-----------:|----------------------|----------|-------:|----------|
| 1     | 7001       | 2024-02-01 09:00:00  | debit    | 500    | success  |
| 2     | 7001       | 2024-02-01 09:03:00  | debit    | 700    | success  |
| 3     | 7002       | 2024-02-01 09:05:00  | credit   | 1200   | success  |
| 4     | 7001       | 2024-02-01 09:07:00  | debit    | 2000   | failed   |
| 5     | 7003       | 2024-02-01 09:10:00  | debit    | 300    | success  |
| 6     | 7001       | 2024-02-01 09:40:00  | debit    | 900    | success  |

## Tasks (7)
1. Net amount by account  
2. Failed txn rate  
3. Latest txn per account  
4. Running balance approximation  
5. Rapid repeat debits within 5 mins  
6. Deduplicate duplicated txns  
7. Second highest successful debit amount

## Solutions
```sql
-- 1 net amount
SELECT account_id,
  SUM(CASE WHEN txn_type='credit' THEN amount ELSE -amount END) AS net_amount
FROM transactions
WHERE status='success'
GROUP BY account_id;
```

```sql
-- 2 failed rate
SELECT 100.0*SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END)/COUNT(*) failed_rate
FROM transactions;
```

```sql
-- 3 latest txn per account
SELECT account_id, txn_id, txn_time, amount, status
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY account_id ORDER BY txn_time DESC, txn_id DESC) rn
  FROM transactions
) t
WHERE rn=1;
```

```sql
-- 4 running net by account
SELECT account_id, txn_time, txn_id,
  SUM(CASE WHEN txn_type='credit' THEN amount ELSE -amount END)
  OVER (PARTITION BY account_id ORDER BY txn_time, txn_id) AS running_net
FROM transactions
WHERE status='success';
```

```sql
-- 5 rapid repeat debits within 5 min
WITH x AS (
  SELECT *, LAG(txn_time) OVER (PARTITION BY account_id ORDER BY txn_time) prev_t
  FROM transactions
  WHERE txn_type='debit' AND status='success'
)
SELECT *
FROM x
WHERE prev_t IS NOT NULL
  AND txn_time - prev_t <= INTERVAL '5 minute';
```

```sql
-- 6 dedup
SELECT *
FROM (
  SELECT *, ROW_NUMBER() OVER (
    PARTITION BY account_id, txn_time, txn_type, amount
    ORDER BY txn_id
  ) rn
  FROM transactions
) t
WHERE rn=1;
```

```sql
-- 7 second highest successful debit (without LIMIT)
SELECT MAX(amount) second_highest_debit
FROM transactions
WHERE txn_type='debit' AND status='success'
  AND amount < (
    SELECT MAX(amount)
    FROM transactions
    WHERE txn_type='debit' AND status='success'
  );
```

## Variations / Edge Cases
- Reversal transactions.
- Multi-currency conversions.
- Eventual consistency between auth and settlement systems.

## Performance Considerations
- Index `(account_id, txn_time, status, txn_type)`.
- Partition by txn_date.
- Build fraud features in incremental pipeline.

## 🔥 Interview Questions
**Basic:** latest transaction per account.  
**Advanced:** anomaly detection and rapid-fire patterning with windows.  
**Product scenario:** card fraud rule design using SQL features.  
**Follow-up:** false positives, delayed settlement, ledger reconciliation.

## Common Mistakes
- Mixing failed txns into balances.
- No deterministic ordering in running windows.
- Ignoring reversals/refunds.
