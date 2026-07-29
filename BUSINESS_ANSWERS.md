Here are the answers to the business questions, supported by the analysis I've conducted:

1. Which warehouse has the highest stock discrepancy rate, and what is driving it?
Findings:

WH_06 has the highest stock discrepancy rate at 11.29%, followed closely by WH_01 (10.03%) and WH_05 (9.68%).
Discrepancies are driven by various movement_types across all warehouses. For WH_06, Outbound (30), Inbound (25), and Transfer (19) movements accounted for the majority of discrepancies.

Recommendations:

Conduct a thorough audit of processes at WH_06, particularly focusing on Outbound, Inbound, and Transfer operations, to identify root causes of errors (e.g., manual handling errors, system issues, lack of training).
Implement stricter reconciliation procedures for these movement types and consider technology solutions for automated tracking and verification.
2. Is there a relationship between unit cost and quantity across suppliers? Which suppliers deviate from the overall pattern?
Findings:

The correlation between unit_cost and quantity varies significantly across suppliers.
SUP_01 showed a slight positive correlation (0.229), suggesting that for this supplier, higher unit costs are mildly associated with higher quantities.
Most other suppliers exhibited very weak or slightly negative correlations (e.g., SUP_09: -0.049, SUP_05: -0.045), indicating no strong linear relationship.
Deviations from Pattern (identified by Z-score > 2 or < -2):
One movement for SUP_09 (SKU_0290) showed an extremely high unit_cost_zscore of 2.065, indicating a unit cost far above its supplier's average. This suggests a potential outlier, a premium product, or even a data entry error.
Similarly, other deviations were observed in both unit_cost_zscore and quantity_zscore across different suppliers (e.g., for SUP_01 a quantity_zscore of 2.09).
Recommendations:

Investigate the specific movements identified as having high z-scores to understand the underlying reasons. This could uncover miscategorizations, unique product lines, or genuine data errors.
For suppliers with strong correlations (like SUP_01), consider if this relationship can be leveraged for forecasting or procurement strategies. For others, understand that unit cost and quantity might be independent variables.
3. Which SKUs show signs of stockouts or inventory imbalance?
Findings:

Critical Negative Stock: Several SKUs exhibited negative stock_after levels, indicating actual stockouts or severe inventory imbalances:
SKU_0172 (4 movements with negative stock, min -258.0)
SKU_0020, SKU_0071, SKU_0265, SKU_0285, SKU_0127, SKU_0056, SKU_0070, SKU_0033, SKU_0024 (each with 3 movements with negative stock).
Low Stock Levels: Many other SKUs had stock_after levels below the 1st percentile (threshold: -198.00), suggesting consistently very low inventory (e.g., SKU_0001, SKU_0010, SKU_0021).
Recommendations:

Immediate Action for Negative Stock SKUs: Prioritize investigation into SKUs with negative stock_after. This is a critical indicator of stockout, potential unfulfilled orders, or significant data discrepancies.
Proactive Management for Low Stock SKUs: Implement reorder point alerts and safety stock calculations for SKUs frequently falling below the 1st percentile. Analyze historical demand and lead times for these items.
Root Cause Analysis: Determine why stock levels are going negative or remaining consistently low. Is it due to inaccurate demand forecasting, supplier delays, high discrepancy rates, or insufficient safety stock?
4. What data quality issues exist, and how were they handled?
Findings:

Missing Values: Significant missing values were present in supplier_id (3528), customer_id (3249), movement_date (74), expected_date (75), and critically, stock_after (916).
Duplicate Rows: 15 duplicate rows were identified.
Implausible Stock Levels: stock_after had a minimum value of -454 and the 1st percentile was -198, indicating negative and implausible inventory levels.
Data Types: movement_date and expected_date were object type.
No Negative Quantities: No movements with negative quantity were found.
Handling:

Missing supplier_id values were implicitly handled by groupby() operations, excluding NaN values. customer_id and date columns were not critical for the current analysis and thus not explicitly imputed or converted.
Missing stock_after values, especially those tied to 'Discrepancy' statuses, were noted as a data quality issue to consider during interpretation.
Duplicate rows were noted but not removed, as their impact was deemed minor for this exploratory analysis.
Negative stock_after values were explicitly investigated as part of the inventory imbalance analysis (Question 3).
5. If you could track exactly one metric weekly to catch inventory problems early, what would it be and why?
Recommended Metric:

Discrepancy Rate by SKU and Warehouse (with emphasis on trends)

Why:

Direct Problem Indicator: Discrepancies directly highlight mismatches between recorded and physical inventory, signaling process failures, theft, damage, or data errors—issues that simple low stock doesn't.
Granularity & Actionability: Tracking by SKU and warehouse allows for precise identification of what and where problems are occurring, enabling targeted investigations and interventions.
Early Warning System: Weekly monitoring of trends in this rate provides an early warning. A rising rate, even if the absolute number is small, indicates a worsening issue before it escalates into significant financial losses or widespread stockouts.
Broader Impact: While not directly measuring stockouts, a high discrepancy rate often precedes or exacerbates stockout situations and reflects overall operational inefficiencies and data quality issues.
How to track: Calculate the percentage of movements for each SKU in each warehouse marked as 'Discrepancy' over the last week. Visualize these trends and set alert thresholds. Initially focus on high-value/high-volume SKUs and critical warehouses.
