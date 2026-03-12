import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:504115868738:CloudPulse_Alerts"
table = dynamodb.Table('CloudPulse_Insights')


def get_running_instances():
    
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            }
        ]
    )

    instance_ids = []

    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_ids.append(instance['InstanceId'])

    return instance_ids


def get_cpu_metrics(instance_id):

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)

    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average']
    )

    datapoints = response['Datapoints']

    if not datapoints:
        return 0

    avg_cpu = sum([point['Average'] for point in datapoints]) / len(datapoints)

    return round(avg_cpu, 2)


def get_recent_cpu_metrics(instance_id):

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)

    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            }
        ],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average']
    )

    return response['Datapoints']


def predict_future_cpu(datapoints):

    if not datapoints:
        return 0

    datapoints = sorted(datapoints, key=lambda x: x['Timestamp'])

    last_values = datapoints[-5:]

    predicted_cpu = sum([p['Average'] for p in last_values]) / len(last_values)

    return round(predicted_cpu, 2)


def classify_instance(cpu):

    if cpu < 20:
        return "Underutilized", "Consider stopping instance to save cost"

    elif cpu <= 70:
        return "Healthy", "No action required"

    else:
        return "Overutilized", "Consider upgrading instance type"


def lambda_handler(event, context):

    instance_ids = get_running_instances()

    results = []

    for instance_id in instance_ids:

        cpu_avg = get_cpu_metrics(instance_id)
        print(f"DEBUG → {instance_id} CPU: {cpu_avg}")
        classification, recommendation = classify_instance(cpu_avg)

        recent_data = get_recent_cpu_metrics(instance_id)

        predicted_cpu = predict_future_cpu(recent_data)

        table.put_item(
            Item={
                "Instance_ID": instance_id,
                "Timestamp": str(datetime.utcnow()),
                "Average_CPU_Last_7_Days": str(cpu_avg),
                "Predicted_CPU": str(predicted_cpu),
                "Classification": classification,
                "Recommendation": recommendation
            }
        )

        if classification == "Overutilized":

            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject="CloudPulse Alert: EC2 Instance Overutilized",
                Message=f"""
CloudPulse Monitoring Alert

Instance ID: {instance_id}

Average CPU (Last 7 Days): {cpu_avg}%
Predicted CPU (Next Hours): {predicted_cpu}%

Status: Overutilized

Recommendation:
{recommendation}

Timestamp: {datetime.utcnow()}
"""
            )

        results.append({
            "Instance_ID": instance_id,
            "Average_CPU_Last_7_Days": cpu_avg,
            "Predicted_CPU_Next_Hours": predicted_cpu,
            "Classification": classification,
            "Recommendation": recommendation
        })

    return {
        "Total_Instances_Processed": len(results),
        "Results": results
    }