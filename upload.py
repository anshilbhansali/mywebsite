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
	tech_articles = dynamodb.Table('tech_articles')
	current_market_articles = dynamodb.Table('current_market_articles')
	personal_finance_articles = dynamodb.Table('personal_finance_articles')

	for id, item in data.iteritems():
		all_articles.put_item(Item=item)
		#if item['category']=='Technology': tech_articles.put_item(Item=item)
		#elif item['category']=='Current Markets': current_market_articles.put_item(Item=item)
		#elif item['category']=='Personal Finance': personal_finance_articles.put_item(Item=item)
		#else: raise Exception('Must Have a valid category, provided: '+item['category'])

print 'done'

