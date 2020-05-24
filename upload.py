import json
from datetime import datetime
import boto3

ACCESS_KEY = None
SECRET_KEY = None

with open('config.json') as f:
	data = json.load(f)
	ACCESS_KEY = data['access_key']
	SECRET_KEY = data['secret_key']

dynamodb = boto3.resource(
	'dynamodb',
	aws_access_key_id=ACCESS_KEY,
	aws_secret_access_key=SECRET_KEY,
	region_name='us-east-2')

with open('fake_data_v2.json') as f:
	data = json.load(f)

	all_articles = dynamodb.Table('all_articles')
	for id, item in data.iteritems():
		all_articles.put_item(Item=item)

print 'done'

