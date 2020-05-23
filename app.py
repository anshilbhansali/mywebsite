from flask import Flask
from flask import render_template
import random
import json
import boto3
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

s3 = boto3.client('s3',
	aws_access_key_id=ACCESS_KEY,
	aws_secret_access_key=SECRET_KEY
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
	tech_keys = [o['Key'] for o in s3.list_objects_v2(Bucket=BUCKET, Prefix='articles/technology/latest-order/').get('Contents', [])]
	cm_keys = [o['Key'] for o in s3.list_objects_v2(Bucket=BUCKET, Prefix='articles/current_markets/latest-order/').get('Contents', [])]
	pf_keys = [o['Key'] for o in s3.list_objects_v2(Bucket=BUCKET, Prefix='articles/personal_finance/latest-order/').get('Contents', [])]
	
	tech_keys = tech_keys[:5]
	cm_keys = cm_keys[:5]
	pf_keys = pf_keys[:5]

	keys = tech_keys+cm_keys+pf_keys
	articles = []
	for key in keys:
		article = json.loads(s3.get_object(Bucket=BUCKET,Key=key)['Body'].read())
		article['created_display'] = format_created(article['created'])
		articles.append(article)

	articles.sort(key=lambda x: x['created'], reverse=True)
	return render_template('index.html',
		articles=articles,
		category="home",
		title="Home",
		lowerize=lowerize
		)

@app.route('/articles/<category>')
def articles(category):
	category = category.lower().replace(" ", "_")
	if category not in VALID_CATEGORIES:
		raise Exception('Must be a valid category: {}'.format(category))

	keys = [o['Key'] for o in s3.list_objects_v2(Bucket=BUCKET, Prefix='articles/{}/latest-order/'.format(category)).get('Contents', [])]

	articles = []
	for key in keys:
		article = json.loads(s3.get_object(Bucket=BUCKET,Key=key)['Body'].read())
		article['created_display'] = format_created(article['created'])
		articles.append(article)

	title = titalize(category)
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

@app.route('/article/<category>/<id>')
def article(category, id):
	category = category.lower().replace(" ", "_")
	if category not in VALID_CATEGORIES:
		raise Exception('Must be a valid category: {}'.format(category))

	key = 'articles/{}/by-id/{}.json'.format(category, id)
	article = json.loads(s3.get_object(Bucket=BUCKET,Key=key)['Body'].read())
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
