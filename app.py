from flask import Flask
from flask import render_template
import random
import json

app = Flask(__name__)

# dummy data
'''
{
	<article_id>: {
		'content': [list of str/paragraphs],
		'title': str,
		'subtitle': str,
		'id': int
	},
}
'''

def get_data():
	articles, articles_by_category = None, None
	with open('fake_data.json') as fake_data:
		articles = json.load(fake_data)
		articles_by_category = {
			'technology': [articles[str(i)] for i in range(1, 8)],
			'current_markets': [articles[str(i)] for i in range(8, 15)],
			'personal_finance': [articles[str(i)] for i in range(15, 21)]
		}
	return articles, articles_by_category

def titalize(category):
	''' splits str by _ and then capitalizes each one
	'''
	return " ".join(el.capitalize() for el in category.split('_'))

# PAGES 

@app.route('/')
@app.route('/index')
def index():
	articles, articles_by_category = get_data()

	category = "home"
	title = titalize(category)

	all_articles = []
	for article_id in articles:
		if int(article_id) in range(1,8):
			articles[article_id]['category'] = "Technology"
		elif int(article_id) in range(8, 15):
			articles[article_id]['category'] = "Current Markets"
		elif int(article_id) in range(15, 21):
			articles[article_id]['category'] = "Personal Finance"


		all_articles.append(articles[article_id])

	random.shuffle(all_articles)
	return render_template('index.html', articles=all_articles, category=category, title=title)

@app.route('/articles/<category>')
def articles(category):
	articles, articles_by_category = get_data()
	if category not in articles_by_category.keys():
		raise Exception('Must be a vaild category: {}'.format(category))

	title = titalize(category)
	articles=articles_by_category[category]

	first = random.choice([i for i in range(len(articles))])
	second = random.choice([i for i in range(len(articles)) if i!=first])
	new_articles = [first, second]
	print new_articles
	return render_template('articles.html', articles=articles, category=category, title=title, new_articles=new_articles)

@app.route('/about')
def about():
	category = "about"
	title = titalize(category)
	return render_template('about.html', articles=articles, category=category, title=title)

@app.route('/contact')
def contact():
	category = "contact"
	title = titalize(category)
	return render_template('contact.html', articles=articles, category=category, title=title)

@app.route('/sections/<current_section>')
def sections(current_section):
	return render_template('sections.html', articles=articles, category=current_section)

@app.route('/article/<id>')
def article(id):
	return "Work in progress..."
	id = int(id)
	title = articles[id]['title']
	content = articles[id]['content']
	return render_template('article.html', heading=title, content=content, id=id)

if __name__ == '__main__':
	app.run(debug=True)
