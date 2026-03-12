{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "6b299cac-7a00-4a88-b008-77543cb21ccf",
   "metadata": {},
   "outputs": [],
   "source": [
    "import json\n",
    "import boto3\n",
    "\n",
    "ec2 = boto3.client('ec2')\n",
    "\n",
    "def lambda_handler(event, context):\n",
    "\n",
    "    params = event.get('queryStringParameters', {})\n",
    "\n",
    "    instance_id = params.get('instance_id')\n",
    "    action = params.get('action')\n",
    "\n",
    "    if not instance_id or not action:\n",
    "        return {\n",
    "            \"statusCode\": 400,\n",
    "            \"body\": json.dumps(\"Missing instance_id or action\")\n",
    "        }\n",
    "\n",
    "    try:\n",
    "\n",
    "        if action == \"start\":\n",
    "            ec2.start_instances(InstanceIds=[instance_id])\n",
    "            message = f\"Instance {instance_id} started successfully\"\n",
    "\n",
    "        elif action == \"stop\":\n",
    "            ec2.stop_instances(InstanceIds=[instance_id])\n",
    "            message = f\"Instance {instance_id} stopped successfully\"\n",
    "\n",
    "        else:\n",
    "            return {\n",
    "                \"statusCode\": 400,\n",
    "                \"body\": json.dumps(\"Invalid action\")\n",
    "            }\n",
    "\n",
    "        return {\n",
    "            \"statusCode\": 200,\n",
    "            \"headers\": {\n",
    "                \"Access-Control-Allow-Origin\": \"*\"\n",
    "            },\n",
    "            \"body\": json.dumps({\n",
    "                \"message\": message\n",
    "            })\n",
    "        }\n",
    "\n",
    "    except Exception as e:\n",
    "\n",
    "        return {\n",
    "            \"statusCode\": 500,\n",
    "            \"body\": json.dumps(str(e))\n",
    "        }"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.14.3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
