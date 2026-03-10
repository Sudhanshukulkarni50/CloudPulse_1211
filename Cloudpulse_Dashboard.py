import streamlit as st
import boto3
import pandas as pd

# DynamoDB connection
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
table = dynamodb.Table('CloudPulse_Insights')

# Fetch data
response = table.scan()
data = response['Items']

df = pd.DataFrame(data)

st.title("CloudPulse Monitoring Dashboard")

if not df.empty:

    st.subheader("Latest Instance Insights")

    latest = df.sort_values("Timestamp", ascending=False).iloc[0]

    st.write("Instance ID:", latest["Instance_ID"])
    st.write("Average CPU (7 Days):", latest["Average_CPU_Last_7_Days"])
    st.write("Predicted CPU:", latest["Predicted_CPU"])
    st.write("Status:", latest["Classification"])
    st.write("Recommendation:", latest["Recommendation"])

    st.subheader("Historical Data")
    st.dataframe(df)

else:
    st.write("No data found in DynamoDB")