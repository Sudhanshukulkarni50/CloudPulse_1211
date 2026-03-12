{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "f2f2dbc1-38c5-4827-bede-ecf4ab0e6b02",
   "metadata": {},
   "outputs": [],
   "source": [
    "import boto3\n",
    "import json\n",
    "from decimal import Decimal\n",
    "\n",
    "dynamodb = boto3.resource('dynamodb')\n",
    "table = dynamodb.Table('CloudPulse_Insights')\n",
    "\n",
    "class DecimalEncoder(json.JSONEncoder):\n",
    "    def default(self, obj):\n",
    "        if isinstance(obj, Decimal):\n",
    "            return float(obj)\n",
    "        return super().default(obj)\n",
    "\n",
    "def lambda_handler(event, context):\n",
    "\n",
    "    items = []\n",
    "    response = table.scan()\n",
    "    items.extend(response['Items'])\n",
    "\n",
    "    while 'LastEvaluatedKey' in response:\n",
    "        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])\n",
    "        items.extend(response['Items'])\n",
    "\n",
    "    return {\n",
    "        'statusCode': 200,\n",
    "        'headers': {\n",
    "            \"Content-Type\": \"application/json\",\n",
    "            \"Access-Control-Allow-Origin\": \"*\",\n",
    "            \"Access-Control-Allow-Methods\": \"GET, OPTIONS\",\n",
    "            \"Access-Control-Allow-Headers\": \"Content-Type\"\n",
    "        },\n",
    "        'body': json.dumps(items, cls=DecimalEncoder)\n",
    "    }"
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
