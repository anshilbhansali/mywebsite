from flask import Flask
from flask import render_template

app = Flask(__name__)

articles = {
		1: "How I saved $100k at the age of 24",
		2: "Why I am bullish about Slack",
		3: "My biggest bet - Elasticsearch",
		4: "Evolution of Operating Systems",
		5: "Uber IPO",
		6: "Analyzing a SAAS company",
		7: "My take on personal finance",
		8: "What the hell is the yield curve?"
	}

@app.route('/')
def index():
	return render_template('index.html', articles=articles)

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
	app.run()
