# SQL Interview Questions for Data Engineers (Real-World, Product-Based)

## How Interviewers Evaluate SQL Answers
Interviewers at Amazon/Uber/Netflix usually score SQL answers on:
1. **Correctness**: Does the query return exact expected data?
2. **Scalability**: Will it work on billions of rows?
3. **Clarity**: Can you explain trade-offs and assumptions?
4. **Robustness**: Did you handle nulls, duplicates, and ties?
5. **Business thinking**: Did you connect SQL to product metrics?

## Common Mistakes Candidates Make
- Jumping into code before clarifying grain/timezone/business definition.
- Ignoring tie handling in ranking problems.
- Using expensive DISTINCT everywhere without reason.
- Missing late-arriving data and dedup logic.
- Not discussing partitioning/indexes.

## Pro Tips
- Think out loud: grain → filters → joins → aggregations → edge cases.
- Always state assumptions explicitly.
- Discuss performance before interviewer asks.
- Provide at least one alternative approach.

---

## Sample Tables Used Across Questions

```sql
-- Employees
employees(emp_id, name, dept_id, salary, updated_at)

-- Orders
orders(order_id, customer_id, product_id, category_id, amount, order_ts, status)

-- Users Activity
user_events(user_id, event_ts, event_type, session_id, country, region)

-- Streaming Watch Events (Netflix style)
watch_events(user_id, content_id, region, watch_minutes, event_ts)

-- Products
products(product_id, category_id, product_name, price)

-- Categories
categories(category_id, category_name)

-- Uber Trips
trips(trip_id, rider_id, driver_id, city_id, request_ts, status, fare_amount)

-- Payments
payments(payment_id, order_id, payment_ts, payment_status, amount)

-- Fraud Signals
fraud_events(event_id, user_id, card_id, ip, device_id, event_ts, amount, decision)
```

---

## 1) Second Highest Salary

### Question
Find the second highest salary from the employees table.

### Why Interviewers Ask This
Tests ranking fundamentals, null handling, and edge-case awareness.

### Approach / Thought Process
1. Clarify if duplicates should count once.
2. Use `DENSE_RANK` or distinct ordering.
3. Handle case where second salary does not exist.

### Answer (Detailed)
```sql
WITH ranked AS (
  SELECT salary,
         DENSE_RANK() OVER (ORDER BY salary DESC) AS rnk
  FROM employees
)
SELECT MAX(salary) AS second_highest_salary
FROM ranked
WHERE rnk = 2;
```
If only one unique salary exists, this returns `NULL`, which is usually expected.

### Follow-Up Questions
- How would you return top 3 salaries?
- Difference between `RANK` and `DENSE_RANK`?
- How to optimize this on very large table?

---

## 2) Top N Salaries per Department

### Question
Get top 3 highest paid employees per department.

### Why Interviewers Ask This
Evaluates partitioned ranking and tie handling.

### Approach / Thought Process
1. Partition by department.
2. Order descending salary.
3. Decide tie logic (`ROW_NUMBER` vs `RANK`).

### Answer (Detailed)
```sql
WITH ranked AS (
  SELECT emp_id, dept_id, salary,
         ROW_NUMBER() OVER (PARTITION BY dept_id ORDER BY salary DESC, emp_id) AS rn
  FROM employees
)
SELECT *
FROM ranked
WHERE rn <= 3;
```
Use `RANK` if you want to include ties beyond 3 records.

### Follow-Up Questions
- Include department name with join?
- What if two employees tie at position 3?
- How to do this without window functions?

---

## 3) Latest Record per User

### Question
Find each user’s latest activity record.

### Why Interviewers Ask This
Checks ability to model "latest snapshot" and deterministic ordering.

### Approach / Thought Process
1. Partition by user.
2. Order by event timestamp descending.
3. Resolve tie with secondary column if required.

### Answer (Detailed)
```sql
WITH latest AS (
  SELECT user_id, event_ts, event_type, country,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY event_ts DESC) AS rn
  FROM user_events
)
SELECT user_id, event_ts, event_type, country
FROM latest
WHERE rn = 1;
```

### Follow-Up Questions
- How to handle same timestamp duplicates?
- How to do incremental loads for this logic?
- Can this be optimized using clustering/sort keys?

---

## 4) Deduplication Logic (Event Stream)

### Question
Deduplicate events where same `(user_id, event_type, event_ts)` can appear multiple times.

### Why Interviewers Ask This
Critical production skill for idempotent pipelines.

### Approach / Thought Process
1. Define dedup key.
2. Keep earliest ingest row or latest correction row.
3. Use row_number and filter.

### Answer (Detailed)
```sql
WITH deduped AS (
  SELECT *,
         ROW_NUMBER() OVER (
           PARTITION BY user_id, event_type, event_ts
           ORDER BY event_ts DESC
         ) AS rn
  FROM user_events
)
SELECT *
FROM deduped
WHERE rn = 1;
```
In real pipelines, include ingestion metadata (`ingest_ts`, `source_offset`) in ordering.

### Follow-Up Questions
- Difference between exact duplicate vs business duplicate?
- How would you dedup in streaming?
- How to make this idempotent in daily reruns?

---

## 5) Sessionization (30-Minute Gap)

### Question
Create user sessions where a new session starts if gap between events is more than 30 minutes.

### Why Interviewers Ask This
Tests temporal analytics and advanced window use.

### Approach / Thought Process
1. Order events by user/time.
2. Compare current event with previous using `LAG`.
3. Flag new session and cumulative sum to assign session id.

### Answer (Detailed)
```sql
WITH e AS (
  SELECT user_id, event_ts,
         LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts) AS prev_ts
  FROM user_events
),
f AS (
  SELECT user_id, event_ts,
         CASE
           WHEN prev_ts IS NULL THEN 1
           WHEN event_ts > prev_ts + INTERVAL '30 minutes' THEN 1
           ELSE 0
         END AS new_session_flag
  FROM e
),
s AS (
  SELECT user_id, event_ts,
         SUM(new_session_flag) OVER (
           PARTITION BY user_id ORDER BY event_ts
           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
         ) AS session_num
  FROM f
)
SELECT *
FROM s;
```

### Follow-Up Questions
- How to compute session duration and events/session?
- How to do this in Spark Structured Streaming?
- What if events arrive late?

---

## 6) Gaps and Islands (Consecutive Active Days)

### Question
Find consecutive active day streaks per user.

### Why Interviewers Ask This
Evaluates pattern detection with date arithmetic.

### Approach / Thought Process
1. Convert timestamps to dates.
2. Assign row_number ordered by date.
3. Group by `(activity_date - row_number offset)` pattern.

### Answer (Detailed)
```sql
WITH d AS (
  SELECT DISTINCT user_id, CAST(event_ts AS DATE) AS activity_date
  FROM user_events
),
r AS (
  SELECT user_id, activity_date,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_date) AS rn
  FROM d
),
g AS (
  SELECT user_id, activity_date,
         activity_date - (rn * INTERVAL '1 day') AS grp
  FROM r
)
SELECT user_id,
       MIN(activity_date) AS streak_start,
       MAX(activity_date) AS streak_end,
       COUNT(*) AS streak_days
FROM g
GROUP BY user_id, grp
ORDER BY user_id, streak_start;
```

### Follow-Up Questions
- Return only longest streak per user?
- How to detect weekly streaks?
- How expensive is DISTINCT here?

---

## 7) Rolling 7-Day Average (Orders)

### Question
Compute daily revenue and rolling 7-day average revenue.

### Why Interviewers Ask This
Tests window frame understanding and reporting metrics.

### Approach / Thought Process
1. Aggregate revenue by day.
2. Apply window average over trailing 6 days + current day.
3. Handle missing days if needed with date spine.

### Answer (Detailed)
```sql
WITH daily AS (
  SELECT CAST(order_ts AS DATE) AS dt,
         SUM(amount) AS daily_revenue
  FROM orders
  WHERE status = 'completed'
  GROUP BY 1
)
SELECT dt,
       daily_revenue,
       AVG(daily_revenue) OVER (
         ORDER BY dt
         ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ) AS rolling_7d_avg
FROM daily
ORDER BY dt;
```

### Follow-Up Questions
- Difference between ROWS and RANGE?
- How to include missing calendar dates?
- How to compute rolling median instead of average?

---

## 8) Cohort Analysis (Monthly Retention)

### Question
Build month-0, month-1, month-2 retention by user signup cohort.

### Why Interviewers Ask This
Tests lifecycle analytics and business metric thinking.

### Approach / Thought Process
1. Define cohort month from first event/order.
2. Map each activity month to cohort.
3. Compute `months_since_cohort`.
4. Count distinct users and retention %.

### Answer (Detailed)
```sql
WITH first_seen AS (
  SELECT user_id, DATE_TRUNC('month', MIN(event_ts)) AS cohort_month
  FROM user_events
  GROUP BY 1
),
activity AS (
  SELECT ue.user_id,
         DATE_TRUNC('month', ue.event_ts) AS activity_month,
         fs.cohort_month
  FROM user_events ue
  JOIN first_seen fs ON ue.user_id = fs.user_id
  GROUP BY 1,2,3
),
retention AS (
  SELECT cohort_month,
         EXTRACT(YEAR FROM activity_month) * 12 + EXTRACT(MONTH FROM activity_month)
         - (EXTRACT(YEAR FROM cohort_month) * 12 + EXTRACT(MONTH FROM cohort_month)) AS month_number,
         COUNT(DISTINCT user_id) AS active_users
  FROM activity
  GROUP BY 1,2
)
SELECT *
FROM retention
ORDER BY cohort_month, month_number;
```

### Follow-Up Questions
- How to compute retention percentage?
- How to define cohort using first purchase only?
- How to include churn reactivation?

---

## 9) Amazon Product Scenario: Top-Selling Product per Category

### Question
Find top-selling product in each category based on total completed order amount.

### Why Interviewers Ask This
Combines joins, aggregation, ranking, and product metric interpretation.

### Approach / Thought Process
1. Join orders with products/categories.
2. Filter completed orders.
3. Aggregate sales per product/category.
4. Rank and pick top.

### Answer (Detailed)
```sql
WITH sales AS (
  SELECT p.category_id,
         p.product_id,
         SUM(o.amount) AS total_sales
  FROM orders o
  JOIN products p ON o.product_id = p.product_id
  WHERE o.status = 'completed'
  GROUP BY 1,2
),
ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY total_sales DESC, product_id) AS rn
  FROM sales
)
SELECT category_id, product_id, total_sales
FROM ranked
WHERE rn = 1;
```

### Follow-Up Questions
- Revenue vs quantity sold?
- How to handle returns/cancellations?
- How to materialize this daily efficiently?

---

## 10) Uber Product Scenario: Daily Active Users (DAU)

### Question
Calculate DAU for Uber app using user events.

### Why Interviewers Ask This
Tests KPI definition and grain correctness.

### Approach / Thought Process
1. Clarify definition of "active" event.
2. Group by date and count distinct users.
3. Optional segmentation by city/country.

### Answer (Detailed)
```sql
SELECT CAST(event_ts AS DATE) AS activity_date,
       COUNT(DISTINCT user_id) AS dau
FROM user_events
WHERE event_type IN ('app_open', 'ride_requested', 'ride_completed')
GROUP BY 1
ORDER BY 1;
```

### Follow-Up Questions
- Difference DAU vs WAU/MAU?
- How to compute stickiness DAU/MAU?
- How to avoid double counting from duplicated events?

---

## 11) Netflix Product Scenario: Most Watched Content by Region

### Question
Find top watched content by region based on total watch minutes.

### Why Interviewers Ask This
Checks regional segmentation and ranking for recommendation/product analytics.

### Approach / Thought Process
1. Aggregate watch minutes by region/content.
2. Rank inside region.
3. Return top 1 (or top N).

### Answer (Detailed)
```sql
WITH agg AS (
  SELECT region, content_id, SUM(watch_minutes) AS total_watch_minutes
  FROM watch_events
  GROUP BY 1,2
),
ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (PARTITION BY region ORDER BY total_watch_minutes DESC, content_id) AS rn
  FROM agg
)
SELECT region, content_id, total_watch_minutes
FROM ranked
WHERE rn = 1;
```

### Follow-Up Questions
- Time-windowed top content (last 7 days)?
- Unique viewers vs total watch minutes?
- How to account for autoplay bias?

---

## 12) Find Users with No Orders

### Question
List customers who never placed an order.

### Why Interviewers Ask This
Basic anti-join pattern, common in churn/activation analytics.

### Approach / Thought Process
1. Left join customers to orders.
2. Filter null order side.
3. Alternative with NOT EXISTS.

### Answer (Detailed)
```sql
SELECT c.customer_id
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

### Follow-Up Questions
- Which is faster: LEFT JOIN NULL vs NOT EXISTS?
- Add signup date filters?
- Exclude canceled test accounts?

---

## 13) Conversion Funnel (View → Add to Cart → Purchase)

### Question
Compute funnel conversion counts by day.

### Why Interviewers Ask This
Tests event analytics and conditional aggregation.

### Approach / Thought Process
1. Aggregate flags per user/day.
2. Count users reaching each funnel stage.
3. Compute ratios.

### Answer (Detailed)
```sql
WITH user_day AS (
  SELECT CAST(event_ts AS DATE) AS dt,
         user_id,
         MAX(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS viewed,
         MAX(CASE WHEN event_type = 'add_to_cart' THEN 1 ELSE 0 END) AS added,
         MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchased
  FROM user_events
  GROUP BY 1,2
)
SELECT dt,
       SUM(viewed) AS view_users,
       SUM(CASE WHEN viewed=1 AND added=1 THEN 1 ELSE 0 END) AS add_users,
       SUM(CASE WHEN viewed=1 AND purchased=1 THEN 1 ELSE 0 END) AS purchase_users
FROM user_day
GROUP BY 1
ORDER BY 1;
```

### Follow-Up Questions
- Session-based funnel instead of day-based?
- Ordered funnel vs unordered funnel?
- How to handle multiple purchases?

---

## 14) Churn Detection (No Activity in 30 Days)

### Question
Find users considered churned as of today if no events in last 30 days.

### Why Interviewers Ask This
Tests date filters and lifecycle definitions.

### Approach / Thought Process
1. Find max activity date per user.
2. Compare with current date.
3. Classify churned/non-churned.

### Answer (Detailed)
```sql
WITH last_activity AS (
  SELECT user_id, MAX(CAST(event_ts AS DATE)) AS last_dt
  FROM user_events
  GROUP BY 1
)
SELECT user_id, last_dt
FROM last_activity
WHERE last_dt < CURRENT_DATE - INTERVAL '30 days';
```

### Follow-Up Questions
- Rolling churn weekly?
- Churn by cohort?
- Reactivation handling?

---

## 15) A/B Test Metric Comparison

### Question
Compare average order amount between control and treatment groups.

### Why Interviewers Ask This
Tests experiment analytics and segmentation.

### Approach / Thought Process
1. Join exposure table to orders.
2. Use same time window after exposure.
3. Aggregate by variant.

### Answer (Detailed)
```sql
-- Assume experiment_exposure(user_id, variant, exposure_ts)
SELECT e.variant,
       COUNT(*) AS orders_count,
       AVG(o.amount) AS avg_order_amount,
       SUM(o.amount) AS total_revenue
FROM experiment_exposure e
JOIN orders o
  ON e.user_id = o.customer_id
 AND o.order_ts >= e.exposure_ts
WHERE o.status = 'completed'
GROUP BY 1;
```

### Follow-Up Questions
- How to avoid selection bias?
- Should we use median instead of mean?
- How to compute significance (outside SQL)?

---

## 16) Late Arriving Data Handling

### Question
How do you build daily revenue query resilient to late-arriving orders?

### Why Interviewers Ask This
Measures production data engineering maturity.

### Approach / Thought Process
1. Use event time, not ingestion time.
2. Recompute sliding backfill window (e.g., last 3 days).
3. Merge/upsert results.

### Answer (Detailed)
```sql
SELECT CAST(order_ts AS DATE) AS dt,
       SUM(amount) AS revenue
FROM orders
WHERE status='completed'
  AND order_ts >= CURRENT_DATE - INTERVAL '3 days'
GROUP BY 1;
```
Run this repeatedly and merge into summary table keyed by `dt`.

### Follow-Up Questions
- Why 3 days, not 1?
- How to detect lateness distribution?
- How to build idempotent backfill?

---

## 17) Payment Success Rate by Day

### Question
Compute payment success rate daily.

### Why Interviewers Ask This
Tests ratio metrics and robust denominators.

### Approach / Thought Process
1. Group by day.
2. Numerator = successful payments.
3. Denominator = total attempts.

### Answer (Detailed)
```sql
SELECT CAST(payment_ts AS DATE) AS dt,
       SUM(CASE WHEN payment_status='success' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS success_rate
FROM payments
GROUP BY 1
ORDER BY 1;
```

### Follow-Up Questions
- Segment by payment method?
- Handle retries to avoid inflated denominator?
- Weekly rolling success rate?

---

## 18) Median Order Value

### Question
Find median order amount for completed orders.

### Why Interviewers Ask This
Tests robust statistics and SQL dialect awareness.

### Approach / Thought Process
1. Use percentile function available in warehouse.
2. Clarify approximate vs exact percentile.

### Answer (Detailed)
```sql
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY amount) AS median_order_amount
FROM orders
WHERE status='completed';
```

### Follow-Up Questions
- Approx percentile for big data?
- Median per category?
- Mean vs median trade-offs?

---

## 19) Running Total Revenue

### Question
Show cumulative revenue by day.

### Why Interviewers Ask This
Checks window accumulation usage.

### Approach / Thought Process
1. Build daily revenue.
2. Apply cumulative sum over ordered date.

### Answer (Detailed)
```sql
WITH daily AS (
  SELECT CAST(order_ts AS DATE) AS dt,
         SUM(amount) AS rev
  FROM orders
  WHERE status='completed'
  GROUP BY 1
)
SELECT dt, rev,
       SUM(rev) OVER (ORDER BY dt) AS cumulative_rev
FROM daily
ORDER BY dt;
```

### Follow-Up Questions
- Reset cumulative by month?
- Add cumulative order count too?
- Handle missing days?

---

## 20) New vs Returning Users per Day

### Question
Count new and returning active users each day.

### Why Interviewers Ask This
Tests first-seen logic and user lifecycle breakdown.

### Approach / Thought Process
1. Derive each user first activity date.
2. Join to daily activity.
3. Compare daily date with first date.

### Answer (Detailed)
```sql
WITH first_seen AS (
  SELECT user_id, MIN(CAST(event_ts AS DATE)) AS first_dt
  FROM user_events
  GROUP BY 1
),
daily_active AS (
  SELECT DISTINCT CAST(event_ts AS DATE) AS dt, user_id
  FROM user_events
)
SELECT da.dt,
       SUM(CASE WHEN da.dt = fs.first_dt THEN 1 ELSE 0 END) AS new_users,
       SUM(CASE WHEN da.dt > fs.first_dt THEN 1 ELSE 0 END) AS returning_users
FROM daily_active da
JOIN first_seen fs ON da.user_id = fs.user_id
GROUP BY 1
ORDER BY 1;
```

### Follow-Up Questions
- Weekly version?
- Reactivated users definition?
- How to avoid timezone misclassification?

---

## 21) Rank Products by Category Revenue Share

### Question
For each category, compute product revenue share and rank.

### Why Interviewers Ask This
Tests window division by partition totals.

### Approach / Thought Process
1. Compute product sales.
2. Compute category total with window sum.
3. Divide and rank.

### Answer (Detailed)
```sql
WITH s AS (
  SELECT p.category_id, o.product_id, SUM(o.amount) AS sales
  FROM orders o
  JOIN products p ON o.product_id = p.product_id
  WHERE o.status='completed'
  GROUP BY 1,2
)
SELECT category_id,
       product_id,
       sales,
       sales * 1.0 / SUM(sales) OVER (PARTITION BY category_id) AS revenue_share,
       RANK() OVER (PARTITION BY category_id ORDER BY sales DESC) AS rnk
FROM s;
```

### Follow-Up Questions
- Filter top 20% contributing products?
- Pareto analysis?
- Materialized view strategy?

---

## 22) Identify Orphan Payments

### Question
Find payments that do not map to any order.

### Why Interviewers Ask This
Data quality check pattern.

### Approach / Thought Process
1. Left join payments to orders.
2. Keep null order side.
3. Use for anomaly alerts.

### Answer (Detailed)
```sql
SELECT p.*
FROM payments p
LEFT JOIN orders o ON p.order_id = o.order_id
WHERE o.order_id IS NULL;
```

### Follow-Up Questions
- How to alert and auto-remediate?
- Could this be eventual consistency issue?
- Should we quarantine these records?

---

## 23) Multi-touch Attribution (Last Touch)

### Question
Assign each purchase to the last marketing touch before order.

### Why Interviewers Ask This
Tests temporal join and business modeling.

### Approach / Thought Process
1. Join touches before purchase time.
2. Choose max touch timestamp per order.
3. Aggregate by channel.

### Answer (Detailed)
```sql
-- marketing_touches(user_id, touch_ts, channel)
WITH c AS (
  SELECT o.order_id, o.customer_id, o.order_ts, mt.channel, mt.touch_ts,
         ROW_NUMBER() OVER (
           PARTITION BY o.order_id
           ORDER BY mt.touch_ts DESC
         ) AS rn
  FROM orders o
  JOIN marketing_touches mt
    ON o.customer_id = mt.user_id
   AND mt.touch_ts <= o.order_ts
  WHERE o.status='completed'
)
SELECT channel, COUNT(*) AS attributed_orders
FROM c
WHERE rn=1
GROUP BY 1;
```

### Follow-Up Questions
- First touch vs last touch?
- Time-decay attribution?
- Attribution window limits (e.g., 7 days)?

---

## 24) Detect Duplicate Orders within 5 Minutes

### Question
Detect likely duplicate orders by same customer and amount within 5 minutes.

### Why Interviewers Ask This
Fraud/ops use case with temporal self-join/window logic.

### Approach / Thought Process
1. Order customer purchases.
2. Compare with previous order amount/time.
3. Flag suspicious duplicates.

### Answer (Detailed)
```sql
WITH x AS (
  SELECT order_id, customer_id, amount, order_ts,
         LAG(order_ts) OVER (PARTITION BY customer_id, amount ORDER BY order_ts) AS prev_ts
  FROM orders
  WHERE status='completed'
)
SELECT *
FROM x
WHERE prev_ts IS NOT NULL
  AND order_ts <= prev_ts + INTERVAL '5 minutes';
```

### Follow-Up Questions
- Extend using product_id/card_id?
- False positive mitigation?
- Real-time detection approach?

---

## 25) Monthly Recurring Revenue (Subscription)

### Question
Compute MRR by month from subscriptions table.

### Why Interviewers Ask This
Classic analytics metric with period aggregation.

### Approach / Thought Process
1. Define active subscription in each month.
2. Sum recurring amount.
3. Account upgrades/cancellations/proration.

### Answer (Detailed)
```sql
-- subscriptions(user_id, plan_amount, start_date, end_date)
SELECT DATE_TRUNC('month', d::date) AS month_start,
       SUM(plan_amount) AS mrr
FROM subscriptions s
JOIN generate_series(s.start_date, COALESCE(s.end_date, CURRENT_DATE), interval '1 month') d ON TRUE
GROUP BY 1
ORDER BY 1;
```
Dialect-specific date spine methods may differ.

### Follow-Up Questions
- Net MRR vs Gross MRR?
- Expansion/contraction decomposition?
- Snapshot table vs event table modeling?

---

## 26) City-Level Uber Completion Rate

### Question
Find trip completion rate by city and day.

### Why Interviewers Ask This
Operational metric with segmentation.

### Approach / Thought Process
1. Group trips by city/day.
2. Completion numerator.
3. Attempts denominator.

### Answer (Detailed)
```sql
SELECT city_id,
       CAST(request_ts AS DATE) AS dt,
       SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS completion_rate
FROM trips
GROUP BY 1,2
ORDER BY 2,1;
```

### Follow-Up Questions
- Split by hour?
- Impact of surge on completion?
- Rider vs driver cancellation rates?

---

## 27) Weekly Active Users (WAU) Rolling

### Question
Compute WAU for each date as distinct users active in previous 7 days.

### Why Interviewers Ask This
Complex distinct-in-window pattern.

### Approach / Thought Process
1. Build date spine.
2. Join events within trailing 6 days.
3. Count distinct users.

### Answer (Detailed)
```sql
-- Simplified approach
WITH dates AS (
  SELECT DISTINCT CAST(event_ts AS DATE) AS dt FROM user_events
)
SELECT d.dt,
       COUNT(DISTINCT ue.user_id) AS wau
FROM dates d
JOIN user_events ue
  ON CAST(ue.event_ts AS DATE) BETWEEN d.dt - INTERVAL '6 days' AND d.dt
GROUP BY 1
ORDER BY 1;
```

### Follow-Up Questions
- Performance<create_file>
<path>data
