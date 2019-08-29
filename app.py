from flask import Flask
from flask import render_template

app = Flask(__name__)

articles = {
		1: "How I saved $100k at the age of 24",
		2: "Why I am bullish about Slack",
		3: "My biggest bet - Elasticsearch",
		4: "How I made a 60% return in 2 years",
		5: "Evolution of Operating Systems",
		6: "Uber IPO",
		7: "Analyzing a SAAS company",
		8: "Working in Chicago vs New York city",
		9: "My take on personal finance",
		10: "What the hell is the yield curve?"
	}

# PAGES 
@app.route('/')
def home():
	category = "home"
	title = " ".join(el.capitalize() for el in category.split('_'))
	return render_template('index.html', articles=articles, category=category, title=title)

@app.route('/index')
def index():
	category = "home"
	title = " ".join(el.capitalize() for el in category.split('_'))
	return render_template('index.html', articles=articles, category=category, title=title)

@app.route('/technology')
def technology():
	category = "technology"
	title = " ".join(el.capitalize() for el in category.split('_'))
	return render_template('articles.html', articles=articles, category=category, title=title)

@app.route('/current_markets')
def current_markets():
	category = "current_markets"
	title = " ".join(el.capitalize() for el in category.split('_'))
	return render_template('articles.html', articles=articles, category=category, title=title)

@app.route('/personal_finance')
def personal_finance():
	category = "personal_finance"
	title = " ".join(el.capitalize() for el in category.split('_'))
	return render_template('articles.html', articles=articles, category=category, title=title)

@app.route('/about')
def about():
	category = "about"
	title = " ".join(el.capitalize() for el in category.split('_'))
	return render_template('about.html', articles=articles, category=category, title=title)

@app.route('/contact')
def contact():
	category = "contact"
	title = " ".join(el.capitalize() for el in category.split('_'))
	return render_template('contact.html', articles=articles, category=category, title=title)

@app.route('/sections/<current_section>')
def sections(current_section):
	print "YO: ", current_section
	return render_template('sections.html', articles=articles, category=current_section)

@app.route('/article/<id>')
def article(id):
	id = int(id)
	heading = "Some article heading"
	content = '''
	BLahBlahBlah BLahBlahBlah BLahBlahBlah BLahBlahBlah
	BLahBlahBlah BLahBlahBlah BLahBlahBlah BLahBlahBlah
	BLahBlahBlah BLahBlahBlah BLahBlahBlah BLahBlahBlah
	BLahBlahBlah BLahBlahBlah BLahBlahBlah BLahBlahBlah
	BLahBlahBlah BLahBlahBlah BLahBlahBlah BLahBlahBlah
	BLahBlahBlah BLahBlahBlah BLahBlahBlah BLahBlahBlah
	BLahBlahBlah BLahBlahBlah BLahBlahBlah BLahBlahBlah
	BLahBlahBlah BLahBlahBlah BLahBlahBlah BLahBlahBlah
	BLahBlahBlah BLahBlahBlah BLahBlahBlah BLahBlahBlah
	'''
	return render_template('article.html', heading=articles[id], content=content, id=id)

if __name__ == '__main__':
	app.run(debug=True)
