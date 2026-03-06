import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')