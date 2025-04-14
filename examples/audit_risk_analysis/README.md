# Audit Risk Analysis Example

## 📁 Dataset Source
- **Origin**: Internal audit records (2020-2025) 
- **Columns**:
  - Firm_Name
  - Year
  - High_Risk_Cases
  - Fraud_Cases_Detected
  - Audit_Effectiveness_Score

## 🚀 What This App Does
- Identifies high-risk audit cases
- Visualizes risk patterns across industries
- Predicts risk scores using custom metrics
- Generates actionable reports

## 🛠️ How to Run
```bash
# Install requirements
pip install preswald pandas plotly numpy

# Run locally
preswald run hello.py

# Deploy to Structured Cloud
preswald deploy --target structured --api-key YOUR_KEY hello.py