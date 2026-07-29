📦 Warehouse Inventory Analytics Dashboard

An interactive Streamlit dashboard for analyzing warehouse inventory movements, identifying inventory discrepancies, detecting data quality issues, and generating actionable business insights.

This project was developed as a take-home assignment to demonstrate data analysis, business reasoning, dashboard development, and data storytelling skills.

🌐 Live Dashboard

Dashboard URL: https://inventorymovementsfreightfox-xtxgfwgjpsvrrwgh92ojrx.streamlit.app/

🚀 Features
Interactive Streamlit dashboard
Dynamic filtering by warehouse, region, supplier, SKU, movement type, status, and date
Real-time KPI cards
Interactive Plotly visualizations
Warehouse discrepancy analysis
Supplier cost and quantity analysis
SKU-level inventory analysis
Data quality validation
Automated business insights
Download filtered dataset as CSV
📊 Dashboard Overview
📈 Overview
Total Inventory Movements
Total Warehouses
Total SKUs
Total Suppliers
Average Unit Cost
Total Inventory Value
Overall Discrepancy Rate
Monthly Movement Trends
Movement Type Distribution
Region-wise Inventory Movements
🏢 Warehouse Analysis
Discrepancy Rate by Warehouse
Warehouse Performance Comparison
Movement Type Breakdown
Top SKUs with Discrepancies
Inventory Value Affected
Warehouse-level Business Insights
🚚 Supplier Analysis
Quantity vs Unit Cost Analysis
Supplier Cost Comparison
Supplier Cost Deviations
Average Quantity by Supplier
High-Value Supplier Analysis
📦 SKU Analysis
Top SKUs with Discrepancies
High-Value Inventory
Inventory Value by SKU
Quantity Distribution
Detailed SKU Performance Table
🔍 Data Quality

The dashboard validates the dataset by checking:

Missing values
Duplicate records
Missing supplier/customer IDs where applicable
Missing stock values
Negative inventory records
Invalid inventory calculations

Inventory movement validation rules:

Inbound: stock_after = stock_before + quantity
Outbound: stock_after = stock_before - quantity
Return: stock_after = stock_before + quantity

Invalid records are highlighted for further investigation.

💡 Business Insights

The dashboard summarizes:

Warehouse with the highest discrepancy rate
Movement types driving discrepancies
Supplier pricing anomalies
High-risk SKUs
Inventory health metrics
Actionable operational recommendations
📂 Project Structure
warehouse-inventory-analytics/
│
├── app.py
├── analysis.py
├── utils.py
├── data/
│   └── inventory_movements.csv
├── BUSINESS_ANSWERS.md
├── README.md
├── requirements.txt
└── assets/
🛠️ Tech Stack
Python
Streamlit
Pandas
NumPy
Plotly
⚙️ Installation

Clone the repository:

git clone https://github.com/<your-username>/warehouse-inventory-analytics.git

Navigate to the project directory:

cd warehouse-inventory-analytics

Install dependencies:

pip install -r requirements.txt

Run the application:

streamlit run app.py

The application will be available at:

http://localhost:8501
📈 Business Questions Addressed

This project answers the following business questions using data-driven analysis:

Which warehouse has the highest stock discrepancy rate, and what is driving it?
Is there a relationship between unit cost and quantity across suppliers? Which suppliers deviate from the overall pattern?
Which SKUs show signs of stockouts or inventory imbalance?
What data quality issues exist, and how were they handled?
Which weekly metric should be monitored to detect inventory problems early?

Each answer is supported by calculations, visualizations, and business recommendations documented in BUSINESS_ANSWERS.md.

📊 Data Processing

The application performs:

Date parsing and formatting
Missing value handling
Inventory movement validation
Inventory value calculation (quantity × unit_cost)
Warehouse discrepancy rate calculation
Supplier cost deviation analysis
SKU and warehouse performance aggregation
💡 Key Insights

The dashboard helps operations teams:

Identify warehouses with high inventory discrepancies.
Detect operational bottlenecks across inbound, outbound, transfer, and return processes.
Monitor supplier pricing anomalies.
Identify high-risk SKUs requiring attention.
Improve inventory accuracy through proactive monitoring.
Detect data quality issues before they impact business decisions.
🚀 Deployment

The dashboard is deployed on Streamlit Community Cloud and is publicly accessible.

Live Application: https://inventorymovementsfreightfox-xtxgfwgjpsvrrwgh92ojrx.streamlit.app/

📹 Demo

A 5-minute walkthrough video accompanies this submission, explaining the dashboard, analysis methodology, and key business insights.

👤 Author

Balaji Chennamshetty

B.Tech in Computer Science & Engineering (AI & ML)

Interested in Data Analytics, Business Intelligence, AI, and building data-driven applications.
