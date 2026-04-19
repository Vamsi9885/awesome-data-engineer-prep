# 🧩 Junk Dimension

## 1) Concept Explanation

A junk dimension groups multiple low-cardinality flags/indicators into one compact dimension table.  
Instead of storing many repetitive yes/no/status columns in a fact table, store a single `junk_key`.

Interview framing:
- Junk dimensions reduce fact width and repetition
- Useful for miscellaneous attributes that do not deserve standalone dimensions
- Common in clickstream, order events, support tickets

---

## 2) Text-Based Diagrams

### 2.1 Without junk dimension

```text
fact_order_event
----------------
event_id
date_key
customer_key
is_gift
is_expedited
payment_risk_flag
coupon_applied
channel_type
...
```

### 2.2 With junk dimension

```text
fact_order_event
----------------
event_id
date_key
customer_key
junk_key
event_amount

dim_junk_order_flags
--------------------
junk_key
is_gift
is_expedited
payment_risk_flag
coupon_applied
channel_type
```

---

## 3) Real-World Use Case

### Amazon checkout analytics
Low-cardinality order attributes:
- gift flag
- coupon flag
- fraud risk bucket
- checkout platform (web/app)

These are grouped into a junk dimension to simplify fact design and improve model consistency.

### Uber
Trip-level flags:
- pooled ride indicator
- surge-applied flag
- airport-pickup flag

### Netflix
Playback flags:
- autoplay
- subtitles enabled
- HDR enabled
- connection quality bucket

---

## 4) When to Use / When NOT to Use

### Use when
- Multiple unrelated low-cardinality attributes exist
- Attributes are frequently used together in filters/grouping
- Need to reduce repeated columns in large facts

### Avoid when
- Attribute has high cardinality (should be separate dimension)
- Attributes represent clear business entity requiring its own dimension
- Combination explosion becomes too large/unmanageable

---

## 5) Advantages & Disadvantages

### Advantages
- Reduces fact table width
- Cleaner schema with one FK instead of many flags
- Better reusability and governance of flag combinations
- Can improve compression and query ergonomics

### Disadvantages
- Harder to understand without documentation
- Combination cardinality can grow quickly
- ETL must maintain deterministic combination-to-key mapping

---

## 6) Common Mistakes

1. Putting high-cardinality attributes in junk dimension
2. No deduping of combinations (duplicate rows with same flags)
3. Letting one junk dimension grow across unrelated domains
4. Missing “unknown/default” junk member
5. Not documenting attribute semantics for analysts

---

## 7) Performance Considerations

- Keep junk dimensions small and indexed by junk_key
- Deduplicate combinations before key generation
- Monitor cardinality growth; split if necessary
- Use dictionary encoding/compression benefits
- Materialize common decoded views for BI ease

---

## 8) 🔥 Interview Questions

### Conceptual
1. What is a junk dimension and why use it?
2. How is junk dimension different from degenerate dimension?
3. What attributes should not go into a junk dimension?

### Scenario-based
1. Your fact has 25 boolean flags. What design do you propose?
2. Junk dimension cardinality grew from 100 to 2M. What went wrong?
3. Analysts complain junk_key is opaque. How do you improve usability?

### Product-based
1. Design junk dimension for Amazon checkout event flags.
2. Design junk flags for Uber trip quality/risk indicators.
3. Design playback junk attributes for Netflix viewing events.

### Follow-ups
- How do you generate stable junk keys in ETL?
- When do you split one junk dimension into two?
- How do you test unknown/default flag handling?
