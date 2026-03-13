import boto3
import json
from decimal import Decimal

dynamodb      = boto3.resource('dynamodb')
table         = dynamodb.Table('CloudPulse_Insights')
alerts_table  = dynamodb.Table('CloudPulse_Alerts')
hourly_table  = dynamodb.Table('CloudPulse_Hourly')   
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):
    print("EVENT:", json.dumps(event))

    path = (
        event.get('rawPath') or
        event.get('path') or
        event.get('resource') or
        ''
    )

    print("PATH DETECTED:", path)

    if 'alerts' in path:
        items    = []
        response = alerts_table.scan()
        items.extend(response['Items'])
        while 'LastEvaluatedKey' in response:
            response = alerts_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        items.sort(key=lambda x: x.get('Timestamp', ''), reverse=True)

    elif 'heatmap' in path:
        items    = []
        response = hourly_table.scan()
        items.extend(response['Items'])
        while 'LastEvaluatedKey' in response:
            response = hourly_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        items.sort(key=lambda x: x.get('Hour_Timestamp', ''))

    else:
        items    = []
        response = table.scan()
        items.extend(response['Items'])
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(items, cls=DecimalEncoder)
    }
