import csv
import numpy as np
from sklearn.svm import SVR
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


app = Flask(__name__)

app.config.update(dict(
    SECRET_KEY='c89nciudf8309ccjk34hifj'
))

companies = {
	"tesla" : "TSLA.csv",
	"facebook" : "FB.csv",
	"oracle" : "ORCL.csv",
	"hp" : "HPE.csv",
	"google" : "GOOGL.csv"
}

cripto = {
	"bitcoin" : "BIT.csv",
	"ethereum" : "ETH.csv",
}

global dates, prices, trade_data, graph_data
dates = []
prices = []
trade_data = []
graph_data = []
graph_dates = []

def get_data(filename):
	global dates, prices, trade_data, graph_data
	dates = []
	prices = []
	trade_data = []
	graph_data = []

	with open(filename, 'r') as file:
		i = 0
		csvFile = csv.reader(file)
		next(csvFile)
		for data in csvFile:
			if i >= 13:
				trade_data.append(data[0:3])
				graph_data.append([str(data[0]), float(data[1])])
			dates.append(int(data[0].split("/")[0]))
			prices.append(float(data[1]))
			i += 1
	return

def get_cripto_data(filename):
	global dates, prices, trade_data, graph_data
	dates = []
	prices = []
	trade_data = []
	graph_data = []

	with open(filename, 'r') as file:
		i = 0
		csvFile = csv.reader(file)
		next(csvFile)
		for data in csvFile:
			if i >= 48:
				trade_data.append(data)
				graph_data.append([str(data[0]), float(data[1])])
			dates.append(i)
			prices.append(float(data[1]))
			i += 1
	return


def predict(dates, prices, x):
	dates = np.reshape(dates, (len(dates), 1))

	#Radial Basis Function Kernel
	svm = SVR(kernel = 'rbf', C = 1e3, gamma = 0.1)
	svm.fit(dates, prices)

	return svm.predict(x)

@app.route("/")
def root():
	return redirect(url_for('index', company="tesla"))

@app.route("/<company>", methods=['GET', 'POST'])
def index(company):
	global dates, prices, trade_data, graph_data
	recomendation = ""

	if not session.get('logged_in'):
		return redirect(url_for('login'))

	if company in companies.keys():		
		get_data(companies[company])
		predictions = []
		aux = []
		for x in trade_data:
			predictions.append(float(predict(dates, prices, int(x[0].split("/")[0]))))
		for i, j in enumerate(graph_data):
			aux.append([j[0], j[1], predictions[i]])

		latest_close = trade_data[len(trade_data)-1][2]
		prediction = predict(dates, prices, int(trade_data[len(trade_data)-1][0].split("/")[0])+4)

		print latest_close, prediction[0]

		reco = ((float(prediction)-float(latest_close))/float(latest_close))*100

		if reco < -10:
			recomendation = "sell stock."
		elif reco >= -5 and reco <= 5:
			recomendation = "hold on your stocks."
		elif reco < -5 and reco >= -10:
			recomendation = "consider selling stock."
		elif reco > 5 and reco <= 10:
			recomendation = "consider buying more stock."
		elif reco > 10:
			recomendation = "buy more stock."

		print reco, recomendation

		return render_template('app.html', trade_data=trade_data, predictions=predictions,
											title=company.title(), graph_data=aux, recomendation=recomendation,
											cripto=False, username="demo")

	elif company in cripto.keys():
		get_cripto_data(cripto[company])
		predictions = []
		aux = []
		for i, j in enumerate(trade_data):
			predictions.append(float(predict(dates, prices, 48+i)))
		for i, j in enumerate(graph_data):
			aux.append([j[0], j[1], predictions[i]])
		latest_close = trade_data[len(trade_data)-1][1]
		prediction = predict(dates, prices, len(trade_data)+4)

		print latest_close, prediction[0]

		reco = ((float(prediction)-float(latest_close))/float(latest_close))*100

		if reco < -10:
			recomendation = "sell currency."
		elif reco >= -5 and reco <= 5:
			recomendation = "hold on to your currency."
		elif reco < -5 and reco >= -10:
			recomendation = "consider selling currency."
		elif reco > 5 and reco <= 10:
			recomendation = "consider buying more currency."
		elif reco > 10:
			recomendation = "buy more currency."

		print reco, recomendation

		return render_template('app.html', trade_data=trade_data, predictions=predictions,
											title=company.title(), graph_data=aux, recomendation=recomendation,
											cripto=True, username="demo")

	return abort(404)

@app.route("/login", methods=['GET', 'POST'])
def login():
	error = None
	if request.method == "POST":
		if request.form['username'] != "demo":
			error = 'Invalid username'
		elif request.form['password'] != "demo":
			error = 'Invalid password'
		else:
			session['logged_in'] = True
			flash('You were logged in')
			return redirect(url_for('index', company="tesla"))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('root'))


if __name__ == "__main__":
	app.run(debug=True)