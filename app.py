from flask import Flask
from flask import render_template
import random
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from datetime import datetime

app = Flask(__name__)

ACCESS_KEY = None
SECRET_KEY = None
BUCKET = None
VALID_CATEGORIES = set(['technology', 'current_markets', 'personal_finance'])

with open('config.json') as f:
	data = json.load(f)
	ACCESS_KEY = data['access_key']
	SECRET_KEY = data['secret_key']
	BUCKET = data['bucket']

dynamodb = boto3.resource(
	'dynamodb',
	aws_access_key_id=ACCESS_KEY,
	aws_secret_access_key=SECRET_KEY,
	region_name='us-east-2'
	)

month_map = {
	1: "January",
	2: "February",
	3: "March",
	4: "April",
	5: "May",
	6: "June",
	7: "July",
	8: "August",
	9: "September",
	10: "October",
	11: "November",
	12: "December",
}

def format_created(created):
	''' Input: datetime string in format YYYY-MM-DD H:M:S
		Output: Nov 28, 2018 
	'''
	created = datetime.strptime(created, '%Y-%m-%d %H:%M:%S').date()
	day, month, year = created.day, created.month, created.year
	month = month_map[month][:3]
	return '{} {}, {}'.format(month, day, year)

titalize = lambda c: " ".join(el.capitalize() for el in c.split('_'))
lowerize = lambda c: c.lower().replace(" ", "_")

@app.route('/')
@app.route('/index')
def index():
	articles = []

	all_articles_table = dynamodb.Table('all_articles')
	for category in VALID_CATEGORIES:
		results = all_articles_table.query(
			KeyConditionExpression=Key('category').eq(titalize(category)),
			ScanIndexForward=False, # sort in descending order of created
			Limit=15
			)
		for item in results['Items']: articles.append(item)

	articles.sort(key=lambda x: x['created'], reverse=True)
	articles = articles[:15]
	
	for article in articles:
		article['created_display'] = format_created(article['created'])

	return render_template('index.html',
		articles=articles,
		category="home",
		title="Home",
		lowerize=lowerize
		)

@app.route('/articles/<category>')
def articles(category):
	category = lowerize(category)
	if lowerize(category) not in VALID_CATEGORIES:
		raise Exception('Must be a valid category: {}'.format(category))

	all_articles = dynamodb.Table('all_articles')
	results = all_articles.query(
		KeyConditionExpression=Key('category').eq(titalize(category)),
		ScanIndexForward=False,
		Limit=15
		)

	articles = []
	for item in results['Items']:
		item['created_display'] = format_created(item['created'])
		articles.append(item)

	new_articles = [articles[0], articles[1]]
	return render_template('articles.html',
		articles=articles,
		category=category,
		title=titalize(category),
		new_articles=new_articles,
		lowerize=lowerize
		)

@app.route('/about')
def about():
	category = "about"
	return render_template('about.html', articles=articles, category=category, title=titalize(category))

@app.route('/sections/<current_section>')
def sections(current_section):
	return render_template('sections.html', articles=articles, category=lowerize(current_section))

@app.route('/article/<category>/<created>')
def article(category, created):
	category = lowerize(category)
	if category not in VALID_CATEGORIES:
		raise Exception('Must be a valid category: {}'.format(category))

	all_articles = dynamodb.Table('all_articles')
	response = all_articles.get_item(
		Key={
		'category': titalize(category),
		'created': created
		}
	)
	article = response['Item']
	article['created_display'] = format_created(article['created'])

	return render_template('article.html',
		title=article['title'],
		content=article['content'],
		category=article['category'],
		subtitle=article['subtitle'],
		lowerize=lowerize
		)

if __name__ == '__main__':
	app.run(debug=True)
