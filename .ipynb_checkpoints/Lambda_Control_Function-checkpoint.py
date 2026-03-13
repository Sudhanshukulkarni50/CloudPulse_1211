import boto3
from datetime import datetime, timedelta
from decimal import Decimal

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

hourly_table = dynamodb.Table('CloudPulse_Hourly')

SNS_TOPIC_ARN = "arn:aws:sns:ap-south-1:504115868738:CloudPulse_Alerts"
table        = dynamodb.Table('CloudPulse_Insights')
alerts_table = dynamodb.Table('CloudPulse_Alerts')


def save_hourly_snapshot(instance_id, instance_name, instance_type, region, az, cpu):
    now         = datetime.utcnow()
    hour_ts     = now.strftime('%Y-%m-%d %H:00:00')
    hour_of_day = now.hour

    hourly_table.put_item(Item={
        "Instance_ID":       instance_id,
        "Hour_Timestamp":    hour_ts,
        "Instance_Name":     instance_name,
        "Instance_Type":     instance_type,
        "Region":            region,
        "Availability_Zone": az,
        "CPU":               Decimal(str(cpu)),
        "Hour":              str(hour_of_day),
        "Date":              now.strftime('%Y-%m-%d')
    })


def get_running_instances():
    paginator = ec2.get_paginator('describe_instances')
    instances = []

    for page in paginator.paginate(
        Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
    ):
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                name = 'N/A'
                for tag in instance.get('Tags', []):
                    if tag['Key'] == 'Name':
                        name = tag['Value']
                        break

                instances.append({
                    'InstanceId':       instance['InstanceId'],
                    'InstanceType':     instance.get('InstanceType', 'N/A'),
                    'AvailabilityZone': instance['Placement']['AvailabilityZone'],
                    'Region':           ec2.meta.region_name,
                    'InstanceName':     name
                })

    return instances


def get_cpu_metrics(instance_id):
    end_time   = datetime.utcnow()
    start_time = end_time - timedelta(hours=1)  # change to days=7 after testing

    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average']
    )

    datapoints = response['Datapoints']
    if not datapoints:
        return 0

    avg_cpu = sum([p['Average'] for p in datapoints]) / len(datapoints)
    return round(avg_cpu, 2)


def get_recent_cpu_metrics(instance_id):
    end_time   = datetime.utcnow()
    start_time = end_time - timedelta(hours=24)

    response = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=3600,
        Statistics=['Average']
    )
    return response['Datapoints']


def predict_future_cpu(datapoints, fallback=0):
    if not datapoints:
        return fallback

    datapoints  = sorted(datapoints, key=lambda x: x['Timestamp'])
    last_values = datapoints[-5:]
    predicted   = sum([p['Average'] for p in last_values]) / len(last_values)
    return round(predicted, 2)


def classify_instance(cpu):
    if cpu < 20:
        return "Underutilized", "Consider stopping instance to save cost"
    elif cpu <= 70:
        return "Healthy", "No action required"
    else:
        return "Overutilized", "Consider upgrading instance type"


def save_alert(instance_id, instance_name, instance_type, region, az, cpu_avg, predicted_cpu, recommendation):
    alerts_table.put_item(Item={
        "Instance_ID":       instance_id,
        "Timestamp":         str(datetime.utcnow()),
        "Instance_Name":     instance_name,
        "Instance_Type":     instance_type,
        "Region":            region,
        "Availability_Zone": az,
        "CPU_At_Alert":      Decimal(str(cpu_avg)),
        "Predicted_CPU":     Decimal(str(predicted_cpu)),
        "Alert_Type":        "Overutilized",
        "Recommendation":    recommendation,
        "SNS_Sent":          "true"
    })


def lambda_handler(event, context):
    instances     = get_running_instances()
    results       = []
    processed_ids = []

    for instance in instances:
        instance_id   = instance['InstanceId']
        instance_type = instance['InstanceType']
        az            = instance['AvailabilityZone']
        region        = instance['Region']
        instance_name = instance['InstanceName']

        try:
            cpu_avg = get_cpu_metrics(instance_id)
            classification, recommendation = classify_instance(cpu_avg)

            recent_data   = get_recent_cpu_metrics(instance_id)
            predicted_cpu = predict_future_cpu(recent_data, fallback=cpu_avg)

            table.put_item(Item={
                "Instance_ID":             instance_id,
                "Instance_Name":           instance_name,
                "Instance_Type":           instance_type,
                "Availability_Zone":       az,
                "Region":                  region,
                "Timestamp":               str(datetime.utcnow()),
                "Average_CPU_Last_7_Days": Decimal(str(cpu_avg)),
                "Predicted_CPU":           Decimal(str(predicted_cpu)),
                "Classification":          classification,
                "Recommendation":          recommendation,
                "Status":                  "running"   
            })

            processed_ids.append(instance_id)

            save_hourly_snapshot(
                instance_id, instance_name, instance_type,
                region, az, cpu_avg
            )

            if classification == "Overutilized":
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject="CloudPulse Alert: EC2 Instance Overutilized",
                    Message=f"""
CloudPulse Monitoring Alert

Instance ID:    {instance_id}
Instance Name:  {instance_name}
Instance Type:  {instance_type}
Region:         {region}
AZ:             {az}

Average CPU:    {cpu_avg}%
Predicted CPU:  {predicted_cpu}%

Status: Overutilized
Recommendation: {recommendation}

Timestamp: {datetime.utcnow()}
"""
                )
                save_alert(
                    instance_id, instance_name, instance_type,
                    region, az, cpu_avg, predicted_cpu, recommendation
                )

            results.append({
                "Instance_ID":    instance_id,
                "Instance_Name":  instance_name,
                "Instance_Type":  instance_type,
                "Region":         region,
                "AZ":             az,
                "Average_CPU":    cpu_avg,
                "Predicted_CPU":  predicted_cpu,
                "Classification": classification,
                "Recommendation": recommendation
            })

        except Exception as e:
            print(f"ERROR processing {instance_id}: {e}")
            continue

    existing = []
    scan_response = table.scan()
    existing.extend(scan_response['Items'])
    while 'LastEvaluatedKey' in scan_response:
        scan_response = table.scan(ExclusiveStartKey=scan_response['LastEvaluatedKey'])
        existing.extend(scan_response['Items'])

    for item in existing:
        if item['Instance_ID'] not in processed_ids:
            table.update_item(
                Key={
                    'Instance_ID': item['Instance_ID'],
                    'Timestamp':   item['Timestamp']
                },
                UpdateExpression='SET #s = :s',
                ExpressionAttributeNames={'#s': 'Status'},
                ExpressionAttributeValues={':s': 'stopped'}
            )

    return {
        "Total_Instances_Processed": len(results),
        "Results": results
    }