# Supply Chain Planning & KPI Optimization Dashboard

A comprehensive supply chain planning cockpit that monitors real business KPIs, process compliance, and provides optimization recommendations for tactical and commercial planning.

## Project Overview

This dashboard simulates a professional supply chain planning system focusing on:
- **Process Compliance Monitoring** - Track planning process adherence and "happy path" performance
- **Supplier Performance Management** - Monitor lead times, quality, and delivery compliance
- **Inventory Optimization** - EOQ, safety stock, and reorder point optimization
- **Demand Forecasting** - ARIMA and Prophet models with accuracy tracking
- **KPI Dashboards** - Real-time monitoring of critical supply chain metrics

## Business Value

### Real-World KPIs Tracked
- **On-Time Delivery (OTD) %** - Supplier delivery performance vs. targets
- **Process Compliance %** - MRP and setup process adherence
- **Forecast Accuracy (MAPE)** - Demand prediction precision
- **Inventory Turnover** - Working capital efficiency
- **Lead Time Variance** - Supplier reliability metrics
- **Defect Rate %** - Quality performance tracking

### Process Improvement Focus
- **Happy Path Analysis** - % of orders following optimal process flow
- **Planning Parameter Standardization** - EOQ, safety stock, ROP optimization
- **Supplier Rationalization** - Performance-based supplier recommendations
- **Inventory Exposure Management** - Overstock and shortage risk mitigation

## Project Structure

```
supply-chain-planning-dashboard/
├── data/                          # Generated datasets
│   ├── orders.csv                # Purchase orders with compliance data
│   ├── inventory.csv             # Current stock levels and parameters
│   ├── products.csv              # Product master data
│   └── suppliers.csv             # Supplier performance data
├── notebooks/                     # Analysis notebooks
│   ├── 01_Process_Compliance_EDA.ipynb
│   └── 02_Forecast_Accuracy_Optimization.ipynb
├── app.py                        # Streamlit planning cockpit
├── utils.py                      # KPI calculation functions
├── data_generator.py             # Synthetic data creation
├── requirements.txt              # Dependencies
└── README.md                     # This file
```

## Quick Start

### Option 1: One-Click Launch
```bash
# Navigate to project directory
cd supply-chain-planning-dashboard

# Generate data and launch dashboard
python data_generator.py
streamlit run app.py
```

### Option 2: Step-by-Step Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic supply chain data
python data_generator.py

# 3. Launch the planning dashboard
streamlit run app.py

# 4. Or explore with Jupyter notebooks
jupyter notebook notebooks/
```

## Dashboard Features

### KPI Monitoring
- **Real-time Metrics** - OTD%, Process Compliance, Defect Rates
- **Trend Analysis** - Monthly performance tracking with targets
- **Alert System** - Critical stock levels and compliance issues

### Performance Analytics
- **Supplier Performance Matrix** - Lead time vs. quality scatter plot
- **ABC Analysis** - Value-based product classification
- **Lead Time Distribution** - Variance analysis vs. targets
- **Compliance Breakdown** - Process adherence by category

### Inventory Management
- **Stock Status Dashboard** - Critical, low, and normal stock levels
- **EOQ vs Current Stock** - Optimization opportunities visualization
- **Reorder Alerts** - Automated recommendations with priorities
- **Exposure Risk Matrix** - Stockout vs. overstock analysis

### Process Compliance
- **Happy Path Tracking** - End-to-end process success rate
- **Non-Compliance Analysis** - Root cause identification
- **Parameter Outlier Detection** - Planning setup standardization

### Optimization Engine
- **Automated Recommendations** - Lead time, quality, and inventory improvements
- **Cost Impact Analysis** - Financial implications of changes
- **Priority Scoring** - Critical, high, medium priority actions

## Advanced Analytics

### Demand Forecasting
- **ARIMA Models** - Time series trend analysis
- **Prophet Integration** - Seasonality and holiday effects
- **Forecast Accuracy Tracking** - MAPE and accuracy metrics
- **Model Comparison** - Automated best model selection

### Inventory Optimization
- **Safety Stock Calculation** - Service level optimization
- **EOQ Optimization** - Carrying cost vs. ordering cost balance
- **Reorder Point Calculation** - Lead time and demand variability
- **ABC Classification** - Pareto-based inventory management

### Process Analytics
- **Happy Path Analysis** - Multi-criteria process success tracking
- **Supplier Scorecards** - Comprehensive performance evaluation
- **Parameter Standardization** - Outlier detection and recommendations
- **Compliance Monitoring** - Process adherence measurement

## Key Insights Generated

### Operational Excellence
- Identify suppliers requiring lead time improvement
- Detect process compliance gaps by category
- Highlight inventory optimization opportunities
- Track forecast accuracy trends

### Financial Impact
- Quantify excess inventory carrying costs
- Calculate potential savings from parameter optimization
- Measure working capital efficiency improvements
- Assess supplier performance impact on costs

### Strategic Recommendations
- Supplier rationalization based on performance
- Process standardization opportunities
- Inventory policy optimization
- Demand sensing improvement areas

## Technical Implementation

### Data Pipeline
- **Synthetic Data Generation** - Realistic supply chain scenarios
- **KPI Calculation Engine** - Real-time metric computation
- **Forecasting Models** - ARIMA and Prophet integration
- **Optimization Algorithms** - EOQ, ROP, and safety stock calculations

### Visualization Stack
- **Streamlit Dashboard** - Interactive planning cockpit
- **Plotly Charts** - Professional business visualizations
- **Pandas Analytics** - Data processing and aggregation
- **Statistical Models** - Time series and optimization

### Business Logic
- **Process Compliance Rules** - Happy path definition and tracking
- **Supplier Performance Metrics** - Multi-dimensional scorecards
- **Inventory Policies** - Automated parameter recommendations
- **Alert Systems** - Exception-based notifications

## Use Cases

### Supply Chain Planners
- Monitor daily KPIs and process compliance
- Identify optimization opportunities
- Track supplier performance trends
- Generate executive reports

### Procurement Teams
- Evaluate supplier performance
- Negotiate lead time improvements
- Assess quality compliance
- Optimize supplier mix

### Inventory Managers
- Monitor stock levels and exposure
- Optimize safety stock policies
- Manage reorder recommendations
- Reduce carrying costs

### Operations Leaders
- Track process standardization
- Monitor forecast accuracy
- Assess working capital efficiency
- Drive continuous improvement

## Future Enhancements

- [ ] **Real-time Data Integration** - ERP system connectivity
- [ ] **Machine Learning Models** - Advanced demand sensing
- [ ] **Multi-location Optimization** - Network-wide planning
- [ ] **Scenario Planning** - What-if analysis capabilities
- [ ] **Mobile Dashboard** - On-the-go monitoring
- [ ] **API Integration** - External system connectivity

## Contact

**Project Showcase** - [GitHub Repository](https://github.com/arvinddharanidharan/supply-chain-planning-dashboard)  
**LinkedIn** - [Your Professional Profile](https://linkedin.com/in/arvinddharanidharan/)  

**This project demonstrates enterprise-level supply chain analytics capabilities, combining process monitoring, predictive analytics, and optimization strategies in a professional dashboard interface.**
