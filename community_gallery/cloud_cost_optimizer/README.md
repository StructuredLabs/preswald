# AWS EC2 Cost Optimization Dashboard

**Deployed Application**: [Cloud Cost Optimizer Dashboard](https://cloud-cost-optimizer-673348-wqgxghno-ndjz2ws6la-ue.a.run.app)

## Dataset Source
The dataset provides a comprehensive comparison of AWS EC2 instance pricing, focusing on different instance types, their specifications, and pricing models. https://instances.vantage.sh/

## Project Overview
The application offers an interactive dashboard for analyzing AWS EC2 instance pricing, helping users identify cost-saving opportunities across various instance types and families.

## Key Features
- Interactive comparison of On-Demand vs Spot instance pricing
- Detailed analysis of cost savings by instance family
- Exploration of instance specifications (vCPUs and Memory)
- Network performance visualization


## 1. Clone the repository
```bash
git clone https://github.com/poorvajasathasivam/preswald.git
cd preswald
```

## 2. Install Dependencies
```bash
pip install -r community_gallery/cloud_cost_optimizer/requirements.txt
```

## 3. Run the Application Locally
```bash
preswald run community_gallery/cloud_cost_optimizer/hello.py
```