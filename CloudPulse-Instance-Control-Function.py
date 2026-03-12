import json
import boto3

ec2 = boto3.client('ec2')

def lambda_handler(event, context):

    params = event.get('queryStringParameters', {})

    instance_id = params.get('instance_id')
    action = params.get('action')

    if not instance_id or not action:
        return {
            "statusCode": 400,
            "body": json.dumps("Missing instance_id or action")
        }

    try:

        if action == "start":
            ec2.start_instances(InstanceIds=[instance_id])
            message = f"Instance {instance_id} started successfully"

        elif action == "stop":
            ec2.stop_instances(InstanceIds=[instance_id])
            message = f"Instance {instance_id} stopped successfully"

        else:
            return {
                "statusCode": 400,
                "body": json.dumps("Invalid action")
            }

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "message": message
            })
        }

    except Exception as e:

        return {
            "statusCode": 500,
            "body": json.dumps(str(e))
        }