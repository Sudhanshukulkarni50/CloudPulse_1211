import boto3
import json
from decimal import Decimal

dynamodb     = boto3.resource('dynamodb')
table        = dynamodb.Table('CloudPulse_Insights')
alerts_table = dynamodb.Table('CloudPulse_Alerts')

# ✅ Decimal encoder — handles Decimal from DynamoDB
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def lambda_handler(event, context):

    # ✅ Handle both HTTP API and REST API path formats
    path = event.get('rawPath') or event.get('path') or '/insights'

    if '/alerts' in path:
        # Fetch from CloudPulse_Alerts table
        items    = []
        response = alerts_table.scan()
        items.extend(response['Items'])
        while 'LastEvaluatedKey' in response:
            response = alerts_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])

        # Sort newest first
        items.sort(key=lambda x: x.get('Timestamp', ''), reverse=True)

    else:
        # Fetch from CloudPulse_Insights table
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
        'body': json.dumps(items, cls=DecimalEncoder)  # ✅ DecimalEncoder fixes the crash
    }