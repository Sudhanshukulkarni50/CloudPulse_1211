import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')

INSTANCE_ID = "i-022d26bb6f22a5bad"

def get_cpu_metrics():

    end_time = date_time.utcnow()
    start_time = end_time - timedelta(days=7)

    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': INSTANCE_ID
            },
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average']
    )
    datapoints = response['Datapoints']

    if not datapoints:
        return "No data"

    avg_cpu = sum([point['Average'] for point in datapoints]) / len(datapoints)

    return round(avg_cpu,2)

def classify_instance(cpu):

    if cpu<20:
        return "Underutilised", "Should stop instance to save cost"
    elif cpu<=70:
        return "Healthy", "No action required"
    else:
        return "Overutilised","Should upgrade instance type"

def lambda_handler(event, context):

    cpu_avg = get_cpu_metric()
    classification, recommendation = classify_instance(cpu_avg)
    
    return {
        "InstanceID":INSTANCE_ID,
        "Average_CPU_Last_7_Days": cpu_avg,
        "Classification": classification,
        "Recommendation": recommendation
    }