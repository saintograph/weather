from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
import datetime
import os
import json
import time
from urllib.request import urlopen

app = Flask(__name__)

# @app.route("/")
# def index():
#     return "Hello World";

# @app.route("/goodbye")
# def goodbye():
#     return "Goodbye, World"

# @app.route("/hello/<name>/<int:age>")
# def hello_name(name, age):
#     return "Hello, {}, you are {} years old".format(name, age)


def get_weather(city):
    url = "http://api.openweathermap.org/data/2.5/forecast/daily?q={}&cnt=10&mode=json&units=metric".format(city)
    response = urlopen(url).read().decode('utf-8')
    return response


@app.route("/")
def index():
    searchcity_raw = request.args.get('searchcity')
    if not searchcity_raw:
        searchcity_raw = request.cookies.get('last_city')
    if not searchcity_raw:
        searchcity_raw = 'Kuala Lumpur'
    # remove whitespaces from query
    searchcity = ''.join(searchcity_raw.split())
    data = json.loads(get_weather(searchcity))
    try:
        city = data['city']['name']
    except KeyError:
        return render_template('invalid_city.html', user_input=searchcity)    
    country = data['city']['country']
    forecast_list = []
    for d in data.get('list'):
        day = time.strftime('%d %B', time.localtime(d.get('dt')))
        mini = d.get('temp').get('min')
        maxi = d.get('temp').get('max')
        description = d.get('weather')[0].get('description')
        forecast_list.append((day, mini, maxi, description))
    response = make_response(render_template('index.html', forecast_list=forecast_list, city=city, country=country))
    if request.args.get('remember'):
        response.set_cookie('last_city', '{}, {}'.format(city, country), expires=datetime.datetime.today() + datetime.timedelta(days=365))
    return render_template('index.html', forecast_list=forecast_list, city=city, country=country)



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='127.0.0.1', port=port, debug=True)
