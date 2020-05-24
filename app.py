from flask import Flask, request
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

DEFAULT_ARTICLE_IMG_1_KEY = 'images/article_img_1.jpg'
DEFAULT_ARTICLE_IMG_2_KEY = 'images/article_img_2.jpg'
PROFILE_PIC_KEY = 'images/profilepic.png'
VALID_CATEGORIES = set(['technology', 'current_markets', 'personal_finance'])
TAG_CLOUD_MAP = {
	"technology": ["software", "cloud computing", "aws", "artificial intelligence", "operating systems", "machine learning", "containers"],
	"current_markets": ["tech companies", "high growth", "direct to consumer", "competitive advantage", "sustainability", "e-commerce"],
	"personal_finance": ["money", "investing", "saving", "budget", "income", "equities", "business", "side hustle"],
}

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

def generate_s3_presigned_url(bucket, key):
	return s3.generate_presigned_url('get_object',
		Params = {
			'Bucket': bucket,
			'Key': key
			},
		ExpiresIn = 1000
		)

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
		article['img_1_url'] = generate_s3_presigned_url(BUCKET, article.get('img1_s3_key', DEFAULT_ARTICLE_IMG_1_KEY))
		article['img_2_url'] = generate_s3_presigned_url(BUCKET, article.get('img2_s3_key', DEFAULT_ARTICLE_IMG_2_KEY))

	profile_pic_url = generate_s3_presigned_url(BUCKET, PROFILE_PIC_KEY)
	profile_bg_url = generate_s3_presigned_url(BUCKET, 'images/bg_4.jpg')

	return render_template('index.html',
		articles=articles,
		category="home",
		title="Home",
		lowerize=lowerize,
		profile_pic_url=profile_pic_url,
		profile_bg_url=profile_bg_url
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
		item['img_1_url'] = generate_s3_presigned_url(BUCKET, item.get('img1_s3_key', DEFAULT_ARTICLE_IMG_1_KEY))
		item['img_2_url'] = generate_s3_presigned_url(BUCKET, item.get('img2_s3_key', DEFAULT_ARTICLE_IMG_2_KEY))
		articles.append(item)

	profile_pic_url = generate_s3_presigned_url(BUCKET, PROFILE_PIC_KEY)
	newsletter_pic_url = generate_s3_presigned_url(BUCKET, 'images/newsletter.jpg')

	new_articles = [articles[0], articles[1]]
	popular_articles = random.sample(articles, 3) # TODO: Some logic behind popular articles
	tags = TAG_CLOUD_MAP[lowerize(category)]

	return render_template('articles.html',
		articles=articles,
		category=category,
		title=titalize(category),
		new_articles=new_articles,
		popular_articles=popular_articles,
		lowerize=lowerize,
		profile_pic_url=profile_pic_url,
		newsletter_pic_url=newsletter_pic_url,
		tags=tags
		)

@app.route('/about')
def about():
	category = "about"
	profile_pic_url = generate_s3_presigned_url(BUCKET, PROFILE_PIC_KEY)
	profile_bg_url = generate_s3_presigned_url(BUCKET, 'images/bg_4.jpg')
	return render_template('about.html',
		articles=articles,
		category=category,
		title=titalize(category),
		profile_pic_url=profile_pic_url,
		profile_bg_url=profile_bg_url
		)

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
	bg_img_url = generate_s3_presigned_url(BUCKET, article.get('bg_img_s3_key', 'images/bg_4.jpg'))

	return render_template('article.html',
		title=article['title'],
		content=article['content'],
		category=article['category'],
		subtitle=article['subtitle'],
		lowerize=lowerize,
		bg_img_url=bg_img_url
		)

@app.route('/subscribe-email', methods=['POST'])
def subscribe_email():
	email = request.values.get('email', None)
	category = request.values.get('category', None)

	if lowerize(category) not in VALID_CATEGORIES:
		raise Exception("Must be a valid category")

	emails_table = dynamodb.Table('emails')
	emails_table.put_item(Item={
		'category': titalize(category),
		'email': email
		})

	ret = {
		'response': email
	}
	return json.dumps(ret)

if __name__ == '__main__':
	app.run(debug=True)
