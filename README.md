# ☁️ CloudPulse
## Serverless EC2 Monitoring & Cost Optimization Platform

🚀 **CloudPulse** is a fully serverless AWS-based monitoring platform that automatically tracks EC2 instance utilization, analyzes CPU usage, sends alerts, and visualizes insights on a real-time dashboard.

The system helps identify **underutilized resources, potential cost savings, and performance issues**, enabling efficient cloud infrastructure management.

---

# 📌 Project Overview

CloudPulse continuously monitors EC2 instances and classifies their health based on CPU usage patterns.

The platform can:

- Monitor EC2 CPU utilization automatically
- Classify instance health (Underutilized / Healthy / Overutilized)
- Predict future CPU usage
- Send automated SNS alerts
- Display infrastructure insights on a real-time dashboard
- Allow users to **start/stop EC2 instances directly from the UI**

This project demonstrates the use of **serverless architecture for cloud monitoring and automation.**

---

# 🏗️ Architecture
EC2 Instances
│
▼
CloudWatch (CPU Metrics)
│
▼
EventBridge (Scheduled Trigger)
│
▼
Lambda (Monitoring & Analysis)
│
▼
DynamoDB
├── CloudPulse_Insights
├── CloudPulse_Alerts
└── CloudPulse_Hourly
│
▼
API Gateway
├── /insights
├── /alerts
├── /heatmap
└── /control
│
▼
S3 Static Dashboard
│
▼
User Interface

SNS → Email Alerts

---

# ☁️ AWS Services Used

| Service | Purpose |
|------|------|
| EC2 | Instances being monitored |
| CloudWatch | Collects CPU utilization metrics |
| Lambda | Serverless compute for monitoring & APIs |
| DynamoDB | Stores monitoring insights and alerts |
| SNS | Sends email alerts |
| API Gateway | Exposes REST APIs |
| S3 | Hosts static dashboard |
| EventBridge | Triggers monitoring Lambda |
| IAM | Handles service permissions |

---

# 🗄️ DynamoDB Tables

## 1. CloudPulse_Insights

Stores monitoring insights for each EC2 instance.

**Primary Key**

Partition Key: `Instance_ID`

Sort Key: `Timestamp`

Fields include:

- Instance_ID
- Instance_Name
- Instance_Type
- Availability_Zone
- Region
- Average_CPU_Last_7_Days
- Predicted_CPU
- Classification
- Recommendation
- Status

---

## 2. CloudPulse_Alerts

Stores alerts generated for overutilized instances.

Fields include:

- Instance_ID
- Instance_Name
- Instance_Type
- CPU_At_Alert
- Predicted_CPU
- Alert_Type
- Recommendation
- SNS_Sent
- Timestamp

---

## 3. CloudPulse_Hourly

Stores hourly CPU metrics used for heatmap visualization.

Fields include:

- Instance_ID
- Instance_Name
- CPU
- Hour
- Date
- Hour_Timestamp

---

# ⚙️ Lambda Functions

## 1️⃣ Main Monitoring Lambda

Triggered by **EventBridge schedule**.

Responsibilities:

- Fetch running EC2 instances
- Retrieve CPU metrics from CloudWatch
- Calculate average CPU utilization
- Predict future CPU usage
- Classify instance health
- Store insights in DynamoDB
- Generate alerts for overutilized instances
- Send SNS notifications

Classification logic:
CPU < 20% → Underutilized
CPU 20–70% → Healthy
CPU > 70% → Overutilized


---

## 2️⃣ Dashboard GET Lambda

Triggered by **API Gateway requests**.

Endpoints handled:
/insights
/alerts
/heatmap


Returns JSON data from DynamoDB for dashboard visualization.

---

## 3️⃣ Instance Control Lambda

Allows EC2 control directly from the dashboard.

Example API requests:

Start instance
/control?instance_id=i-xxxx&action=start

Stop instance

/control?instance_id=i-xxxx&action=stop


---

# 🌐 API Gateway Routes

| Route | Purpose |
|------|------|
| GET /insights | Fetch monitoring insights |
| GET /alerts | Fetch alert history |
| GET /heatmap | Fetch hourly CPU data |
| GET /control | Start or Stop EC2 instance |

---

# 📊 Dashboard Features

### KPI Cards

- Total Instances
- Running Instances
- Underutilized Instances
- Healthy Instances
- Overutilized Instances
- Average CPU (7 days)
- Estimated Monthly Savings

---

### Charts

- CPU Trend Line Chart
- CPU Prediction Bar Chart
- Health Distribution Pie Chart

---

### CPU Heatmap

Visualizes hourly CPU usage.

Rows → EC2 instances  
Columns → Hours (00–23)

Color scale:

Low usage → Blue  
Medium usage → Yellow  
High usage → Red

---

### Instance Table

Displays detailed information:

- Instance ID & Name
- Average CPU
- Predicted CPU
- Classification badge
- Recommendation
- Timestamp
- Start / Stop controls

Additional features:

- Search and filtering
- Stopped instance badge
- Instance detail modal

---

# 🚨 Alert System

When CPU utilization exceeds the threshold:

1. Lambda generates an alert
2. Alert stored in DynamoDB
3. SNS sends email notification

Alert information includes:

- Instance ID
- CPU at alert
- Predicted CPU
- Severity level
- Timestamp

---

# ⚡ Additional Features

- Auto refresh dashboard every 5 minutes
- Global date filtering
- Alert history panel
- Export alerts to CSV
- HTML report generation
- Real-time activity logs
- System status indicator

---

# 📊 Project Statistics

AWS Services Used → **9**

Lambda Functions → **3**

DynamoDB Tables → **3**

API Routes → **4**

Dashboard Features → **15+**

Dashboard Code → **~1200+ lines**

---

# 🎯 Conclusion

CloudPulse demonstrates how a **fully serverless architecture can be used to build a scalable cloud monitoring system.**

The project combines:

- Cloud infrastructure monitoring
- Serverless automation
- Data visualization
- Cost optimization

By leveraging AWS services such as **Lambda, CloudWatch, DynamoDB, API Gateway, SNS, and S3**, CloudPulse provides a powerful and cost-efficient monitoring solution for EC2 workloads.

---

⭐ If you found this project interesting, feel free to explore the repository and contribute.
