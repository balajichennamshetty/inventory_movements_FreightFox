Candidate Name: Balaji Chennamshetty
Date 29/07/2026

Q1. Which warehouse has the highest stock discrepancy rate, and what's actually driving it?
Answer

Warehouse WH_06 recorded the highest stock discrepancy rate at 11.29%, with 89 discrepancy movements out of 788 total movements. This makes WH_06 the warehouse with the greatest inventory accuracy risk.

A breakdown of discrepancy movements shows that the majority originated from:

Outbound: 30 discrepancies (33.7%)
Inbound: 25 discrepancies (28.1%)
Transfer: 19 discrepancies (21.3%)
Adjustment: 9 discrepancies (10.1%)
Return: 6 discrepancies (6.7%)

Nearly 62% of all discrepancies were associated with Outbound and Inbound operations, suggesting that inventory accuracy issues are primarily occurring during receiving and shipping activities. Transfer discrepancies further indicate possible synchronization or scanning issues during inter-warehouse movements.

Recommendation

WH_06 should be prioritized for operational improvements by:

Auditing receiving and shipping workflows.
Increasing cycle-count frequency for high-volume SKUs.
Reviewing barcode scanning and inventory update procedures.
Monitoring weekly discrepancy trends to measure improvement.
Method
Grouped records by warehouse_id.
Counted total movements and discrepancy movements (status = Discrepancy).
Calculated discrepancy rate as:

Discrepancy Rate = (Discrepancies ÷ Total Movements) × 100

Analyzed discrepancy records by movement type to identify operational drivers.
Q2. Is there a relationship between unit cost and quantity across suppliers? Which suppliers deviate, and by how much?
Answer

Supplier-level analysis shows no strong linear relationship between quantity and unit cost. Most suppliers exhibited weak positive or negative correlations, indicating that larger order quantities do not consistently correspond to higher or lower unit costs.

Notable observations include:

SUP_01 showed the strongest positive correlation (r = 0.229), suggesting a slight tendency for larger quantities to be associated with higher unit costs.
SUP_09 (-0.049) and SUP_05 (-0.045) showed almost no relationship between quantity and unit cost.

To identify unusual transactions, I calculated supplier-specific z-scores.

The largest deviations were:

A SUP_09 transaction (SKU_0290) with a unit cost z-score of 2.065, indicating a significantly higher unit cost than the supplier's normal pricing pattern.
A SUP_01 transaction with a quantity z-score of 2.09, representing an unusually large order compared with other transactions from that supplier.

These transactions should be reviewed to determine whether they represent premium products, exceptional purchase orders, or pricing anomalies.

Method
Calculated Pearson correlation between quantity and unit_cost for each supplier.
Computed supplier-level z-scores for quantity and unit cost.
Flagged transactions where |z-score| > 2.
Q3. Which SKUs show signs of inventory imbalance, and what would you recommend?
Answer

Several SKUs repeatedly recorded negative stock_after values, indicating inventory imbalances that require investigation.

The most affected SKUs include:

SKU_0172 – 4 negative inventory movements (minimum stock_after = -258)
SKU_0020
SKU_0071
SKU_0265
SKU_0285
SKU_0127
SKU_0056
SKU_0070
SKU_0033
SKU_0024

These negative inventory values may result from stockouts, delayed inventory updates, transaction timing issues, or inventory recording errors. Regardless of the cause, they represent inventory states that should not occur in a well-controlled warehouse.

Additionally, several SKUs consistently operated below the 1st percentile of inventory levels, suggesting they are at greater risk of future stockouts.

Recommendations
Prioritize cycle counts for the affected SKUs.
Review recent inbound, outbound, and adjustment transactions to identify the source of the imbalance.
Implement SKU-specific reorder points and safety stock levels.
Improve demand forecasting for frequently affected products.
Monitor supplier performance where delays contribute to inventory shortages.
Method
Filtered records where stock_after ≤ 0.
Grouped by sku_id.
Counted negative inventory occurrences.
Calculated the 1st percentile of stock_after to identify consistently low-stock SKUs.
Q4. Before trusting the analysis, what data quality issues were found, and how were they handled?
Answer

Before performing the analysis, several data quality checks were completed.

Findings

Missing Values

supplier_id and customer_id contained many missing values. These were expected because inbound movements reference suppliers while outbound movements reference customers. They were validated against movement_type before being treated as issues.
movement_date (74 missing)
expected_date (75 missing)
stock_after (916 missing), with many missing values occurring alongside discrepancy records.

Duplicate Records

15 duplicate rows were identified.

Inventory Anomalies

Negative stock_after values were detected. These were treated as inventory anomalies requiring operational investigation rather than automatically assuming data errors.

Data Types

movement_date and expected_date were converted to datetime format to enable accurate filtering and time-based analysis.
Handling
Missing supplier/customer values were retained where they were expected based on movement type.
Missing stock_after values were highlighted rather than imputed because they may represent unresolved discrepancy events.
Duplicate rows were identified and flagged. In a production environment, these should be validated before removal.
Inventory anomalies were retained for investigation because they directly answer the business questions.
Method
Missing values using isnull().sum()
Duplicate detection using duplicated().sum()
Summary statistics using describe()
Inventory validation using stock_before, stock_after, and quantity
Q5. If you could track exactly one metric weekly to catch inventory problems early, what would it be?
Answer

I would monitor the Weekly Inventory Discrepancy Rate at the warehouse and SKU level.

Discrepancy Rate = (Discrepancy Movements ÷ Total Movements) × 100

This metric directly measures inventory accuracy and provides an early warning of receiving errors, shipping mistakes, inventory mismatches, and operational process failures.

Tracking this metric weekly enables warehouse managers to:

Detect deteriorating inventory accuracy early.
Identify problematic warehouses or SKUs.
Prioritize investigations before discrepancies become costly.
Measure whether operational improvements are reducing inventory issues over time.

Because it reflects multiple underlying operational problems in a single metric, it provides the clearest and most actionable view of warehouse health.

Additional Recommendations

If this dataset were used in a production warehouse environment, I would also recommend:

Recording stock_after for every discrepancy movement.
Capturing the root cause of each discrepancy (e.g., counting error, damage, theft, shipping error).
Standardizing supplier and customer information.
Implementing automated alerts when discrepancy rates exceed predefined thresholds.
Integrating the dashboard with the Warehouse Management System (WMS) or ERP for real-time monitoring and proactive issue detection.
