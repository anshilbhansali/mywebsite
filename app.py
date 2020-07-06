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
DEFAULT_BG_IMG_KEY = 'images/bg_4.jpg'
DEFAULT_IMG2_WIDTH = 500
DEFAULT_IMG2_HEIGHT = 300

PROFILE_PIC_KEY = 'images/profilepic.png'
VALID_CATEGORIES = set(['technology', 'current_markets', 'personal_finance'])
TAG_CLOUD_MAP = {
	"technology": ["software", "cloud computing", "aws", "artificial intelligence", "operating systems", "machine learning", "containers"],
	"current_markets": ["tech companies", "high growth", "direct to consumer", "competitive advantage", "sustainability", "e-commerce"],
	"personal_finance": ["money", "investing", "saving", "budget", "income", "equities", "business", "side hustle"],
}
NUM_ARTICLES_IN_PAGE = 4

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

cache = {}

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
	profile_bg_url = generate_s3_presigned_url(BUCKET, 'images/spotlight.jpg')

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
	current_page = request.args.get('page', 1)

	category = lowerize(category)
	if lowerize(category) not in VALID_CATEGORIES:
		raise Exception('Must be a valid category: {}'.format(category))

	# FAST CURSOR METHOD FOR PAGINATION
	# Fetch all the keys first
	all_articles = dynamodb.Table('all_articles')
	results = all_articles.query(
		KeyConditionExpression=Key('category').eq(titalize(category)),
		ScanIndexForward=False,
		ProjectionExpression="category, created"
		)
	# Split keys into page-sized chunks
	all_keys = [item for item in results['Items']]
	all_keys_chunks = [all_keys[i:i+NUM_ARTICLES_IN_PAGE] for i in range(0, len(all_keys), NUM_ARTICLES_IN_PAGE)]
	# Identify current chunk and start key
	current_keys_chunk = all_keys_chunks[int(current_page)-1]
	start_key = current_keys_chunk[0]

	pages = [str(i) for i in range(1, len(all_keys_chunks)+1)]
	cache['all_keys'] = all_keys

	# query articles from start_key
	results = all_articles.query(
		KeyConditionExpression=Key('category').eq(start_key['category']) & Key('created').lte(start_key['created']),
		ScanIndexForward=False,
		Limit=NUM_ARTICLES_IN_PAGE
		)

	articles = []
	for item in results['Items']:
		item['created_display'] = format_created(item['created'])
		item['img_1_url'] = generate_s3_presigned_url(BUCKET, item.get('img1_s3_key', DEFAULT_ARTICLE_IMG_1_KEY))
		item['img_2_url'] = generate_s3_presigned_url(BUCKET, item.get('img2_s3_key', DEFAULT_ARTICLE_IMG_2_KEY))
		item['bg_img_url'] = generate_s3_presigned_url(BUCKET, item.get('bg_img_s3_key', DEFAULT_BG_IMG_KEY))

		item['img_url'] = random.choice([item['img_1_url'], item['img_2_url']])

		articles.append(item)

	profile_pic_url = generate_s3_presigned_url(BUCKET, PROFILE_PIC_KEY)
	newsletter_pic_url = generate_s3_presigned_url(BUCKET, 'images/newsletter.jpg')

	new_articles = articles[:2]
	popular_articles = random.sample(articles, min(2, len(articles))) # TODO: Some logic behind popular articles
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
		tags=tags,
		current_page=current_page,
		pages=pages
		)

@app.route('/about')
def about():
	category = "about"
	profile_pic_url = generate_s3_presigned_url(BUCKET, PROFILE_PIC_KEY)
	profile_bg_url = generate_s3_presigned_url(BUCKET, 'images/spotlight.jpg')
	return render_template('about.html',
		articles=articles,
		category=category,
		title=titalize(category),
		profile_pic_url=profile_pic_url,
		profile_bg_url=profile_bg_url
		)

@app.route('/sections/<current_section>')
def sections(current_section):
	return render_template('sections.html',
		articles=articles,
		category=lowerize(current_section))

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
	bg_img_url = generate_s3_presigned_url(BUCKET, article.get('bg_img_s3_key', DEFAULT_BG_IMG_KEY))
	img2_url = generate_s3_presigned_url(BUCKET, article.get('img2_s3_key', DEFAULT_ARTICLE_IMG_2_KEY))
	img2_width = DEFAULT_IMG2_WIDTH if article.get('img2_width', None)==None else article.get('img2_width')
	img2_height = DEFAULT_IMG2_HEIGHT if article.get('img2_height', None)==None else article.get('img2_height')
	print article.get('img2_width', None)

	return render_template('article.html',
		title=article['title'],
		content=article['content'],
		category=article['category'],
		subtitle=article['subtitle'],
		lowerize=lowerize,
		bg_img_url=bg_img_url,
		img2_url=img2_url,
		img2_width=img2_width,
		img2_height=img2_height
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
