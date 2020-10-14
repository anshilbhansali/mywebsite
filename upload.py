import json
from datetime import datetime
import boto3
import shutil

ACCESS_KEY = None
SECRET_KEY = None

with open('config.json') as f:
	data = json.load(f)
	ACCESS_KEY = data['access_key']
	SECRET_KEY = data['secret_key']
	BUCKET = data['bucket']

dynamodb = boto3.resource(
	'dynamodb',
	aws_access_key_id=ACCESS_KEY,
	aws_secret_access_key=SECRET_KEY,
	region_name='us-east-2')

s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

with open('current_article/article.json') as f:
	''' Rules for adding links to words
		format: blah blah blah [word-to-be-linked|link] blah blah
	'''
	data = json.load(f)
	data['created'] = str(datetime.now()).split('.')[0]

	# upload images
	# MAKE SURE PNGS AND JPGS ARE CORRECT
	title = data['title']
	# MUST BE images/<>.jpg or png
	bg, img1, img2 = 'bg.png', 'img1.jpg', 'img2.png'
	img1_s3_key = "images/{}/{}".format(title.lower().replace(' ', ''), img1)
	img2_s3_key = "images/{}/{}".format(title.lower().replace(' ', ''), img2)
	bg_img_s3_key = "images/{}/{}".format(title.lower().replace(' ', ''), bg)
	s3_client.upload_file('current_article/{}'.format(img1), BUCKET, img1_s3_key)
	s3_client.upload_file('current_article/{}'.format(img2), BUCKET, img2_s3_key)
	s3_client.upload_file('current_article/{}'.format(bg), BUCKET, bg_img_s3_key)

	print 'Uploaded images'

	data['img1_s3_key'] = img1_s3_key
	data['img2_s3_key'] = img2_s3_key
	data['bg_img_s3_key'] = bg_img_s3_key

	# guardrails
	if data['category'] not in ('Technology', 'Personal Finance', 'Current Markets'):
		raise Exception('Not a valid category')

	all_articles = dynamodb.Table('all_articles')
	all_articles.put_item(Item=data)
	print 'Uploaded article'
	print json.dumps(data, indent=1)

	source, dest = 'current_article/{}'.format(bg), 'old_bgs/{}-{}'.format(str(datetime.now()), bg)
	shutil.copyfile(source, dest)
	print 'Copied background img to {}'.format(dest)

print 'done'

