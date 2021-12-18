import copy
import sys

import orjson
import requests
import os
import countryinfo
from flask import Flask, jsonify, make_response
from flask_caching import Cache
from flask_cors import CORS

from functions import *
from predict import *

# There are various levels of the debug mode
# 0: Turn off the debug mode
# 1: Show a part of the logs
# Equal or above 2: Show full logs
debug_mode = 2

# Data of the epidemic
world = {}
country = {}

# The last update time of our backend
update = 4102329600.0

# The timestamp of the latest version of the data
if debug_mode > 0:
    print("Fetching the timestamp of the latest version of the data")
latest = getTimestampByStr(orjson.loads(requests.get("https://covid19.who.int/page-data/sq/d/464037013.json").text)["data"]["lastUpdate"]["date"])

# Data of the vaccination
total_vaccinated = 0
plus_vaccinated = 0
fully_vaccinated = 0

for item in countryinfo.country_list:
    country[item] = {}

if not os.path.exists("cache"):
    os.makedirs("cache")

if os.path.exists("cache/update.txt"):
    with open("cache/update.txt", 'r', encoding='utf-8') as file:
        update = float(file.read())

if not os.path.exists("cache/data.json") or latest > update:
    if debug_mode > 0:
        print("Fetching whole datasets from WHO")
    url = "https://covid19.who.int/page-data/measures/page-data.json"
    request = requests.get(url)
    with open("cache/data.json", 'w', encoding='utf-8') as file:
        file.write(request.text)
    with open("cache/update.txt", 'w', encoding='utf-8') as file:
        file.write(str(latest))

with open("cache/data.json", 'r', encoding='utf-8') as file:
    data = orjson.loads(file.read())["result"]["pageContext"]["rawDataSets"]

if debug_mode > 0:
    print("Loading datasets finished")

with open('cache/update.txt', 'w', encoding='utf-8') as file:
    file.write(str(getTimestampByStr(data["lastUpdate"])))

country_list = []

for item in data["countriesCurrent"]["rows"]:
    if item[0] in country:
        country[item[0]]["ISO"] = item[0]
        country[item[0]]["deaths"] = item[1]
        country[item[0]]["cumulative_deaths"] = item[2]
        country[item[0]]["cases"] = item[6]
        country[item[0]]["cumulative_cases"] = item[7]

for item in data["vaccineData"]["data"]:
    key = countryinfo.get_iso(item["ISO3"])
    if key in country:
        country[key]["country"] = item["REPORT_COUNTRY"]
        country[key]["total_vaccinated"] = item["TOTAL_VACCINATIONS"]
        country[key]["plus_vaccinated"] = item["PERSONS_VACCINATED_1PLUS_DOSE"]
        country[key]["fully_vaccinated"] = item["PERSONS_FULLY_VACCINATED"]
        country_list.append({
            "ISO": country[key]["ISO"],
            "name": country[key]["country"]
        })

# Sort the country list by name in order to be compatible to the frontend
country_list = sorted(country_list, key = lambda item: item["name"])

for item in data["vaccineData"]["data"]:
    if item["TOTAL_VACCINATIONS"] is not None:
        total_vaccinated += item["TOTAL_VACCINATIONS"]
    if item["PERSONS_VACCINATED_1PLUS_DOSE"] is not None:
        plus_vaccinated += item["PERSONS_VACCINATED_1PLUS_DOSE"]
    if item["PERSONS_FULLY_VACCINATED"] is not None:
        fully_vaccinated += item["PERSONS_FULLY_VACCINATED"]

for item in data["countryGroups"]:
    if item["value"] in country:
        country[item["value"]]["history"] = []
        for index, row in enumerate(item["data"]["rows"]):
            country[item["value"]]["history"].append({
                "time": getTimeByIndex(index),
                "deaths": row[2],
                "cumulative_deaths": row[3],
                "cases": row[7],
                "cumulative_cases": row[8]
            })

world["history"] = []
world_daily = []

for index, row in enumerate(data["byDay"]["rows"]):
    world_daily.append({"deaths": row[1], "cases": row[6]})

for index, row in enumerate(data["byDayCumulative"]["rows"]):
    world["history"].append({
        "time": getTimeByIndex(index),
        "deaths": world_daily[index]["deaths"],
        "cumulative_deaths": row[1],
        "cases": world_daily[index]["cases"],
        "cumulative_cases": row[6],
    })

world["update"] = getTimestampByStr(data["lastUpdate"])
world["deaths"] = data["today"]["Deaths"]
world["cumulative_deaths"] = data["today"]["Cumulative Deaths"]
world["cases"] = data["today"]["Confirmed"]
world["cumulative_cases"] = data["today"]["Cumulative Confirmed"]
world["total_vaccinated"] = total_vaccinated
world["plus_vaccinated"] = plus_vaccinated
world["fully_vaccinated"] = fully_vaccinated

result = {
    "world": world,
    "country": country
}

predict_inputs = {}

all_case = [0 for index in range(len(result["country"]["US"]["history"]))]
all_death = all_case.copy()

for country in result['country']:
    origin_cases = []
    origin_deaths = []
    for index, item in enumerate(result['country'][country]['history']):
        origin_cases.append(item['cases'])
        origin_deaths.append(item['deaths'])
        all_case[index] += item['cases']
        all_death[index] += item['deaths']
    predict_inputs[country] = {"cases": origin_cases, "deaths": origin_deaths}

predict_inputs["ALL"] = {"cases": all_case, "deaths": all_death}

def fetch_prediction(country, length, look_back):
    if debug_mode > 0:
        print("Getting prediction data of:", country)
    prediction_cache = {}
    # If the cache is exist and not stale then return the result directly
    if os.path.exists("cache/prediction.json"):
        with open("cache/prediction.json", 'r', encoding='utf-8') as file:
            prediction_cache = orjson.loads(file.read())
            if country in prediction_cache:
                if debug_mode > 1:
                    print("Timestamp difference:", getTimeNow() - prediction_cache[country]["time"])
                if getTimeNow() - prediction_cache[country]["time"] < 86400:
                    return prediction_cache[country]["value"]
    # Get the prediction and turn it into frontend compatible style then cache it
    predict_cases = tensorflow_predict(predict_inputs[country]["cases"], country + "_c", length, look_back)
    predict_deaths = tensorflow_predict(predict_inputs[country]["deaths"], country + "_d", length, look_back)
    value = []
    if country == "ALL":
        last_data = result["world"]["history"][-1]
    else:
        last_data = result["country"][country]["history"][-1]
    cumulative_cases, cumulative_deaths, time = last_data["cumulative_cases"], last_data["cumulative_deaths"], last_data["time"]
    for index in range(length):
        cumulative_cases += predict_cases[index]
        cumulative_deaths += predict_deaths[index]
        time += 86400
        value.append({
            "cases": predict_cases[index],
            "cumulative_cases": cumulative_cases,
            "deaths": predict_deaths[index],
            "cumulative_deaths": cumulative_deaths,
            "time": time
        })
    prediction_cache[country] = {
        'time': getTimeNow(),
        'value': value
    }
    with open("cache/prediction.json", 'wb') as file:
        file.write(orjson.dumps(prediction_cache))
    return prediction_cache[country]["value"]

app = Flask(__name__)
app.config.from_mapping({"CACHE_TYPE": "SimpleCache"})
cache = Cache(app)

def make_response_cors(data):
    response = make_response(jsonify(data))
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/')
@cache.cached(timeout = 3600)
def page_index():
    output = copy.deepcopy(result)
    for name in result['country']:
        del output['country'][name]["history"]
    output["status"] = 200
    return make_response_cors(output)

@app.route('/country/<string:country_name>', methods=['GET'])
@cache.cached(timeout = 3600)
def page_country(country_name: str):
    if country_name in result['country']:
        output = copy.deepcopy(result['country'][country_name])
        output["country_list"] = country_list
        return make_response_cors(output)
    else:
        return make_response_cors({"status": 404, "error_msg": "Country not found"})

@app.route('/predict/<string:country_name>', methods=['GET'])
@cache.cached(timeout = 3600)
def predict_country(country_name: str):
    if country_name in result['country'] or country_name == "ALL":
        return make_response_cors(fetch_prediction(country_name, 7, 7))
    else:
        return make_response_cors({"status": 404, "error_msg": "Country not found"})

if __name__ == '__main__':
    CORS(app, supports_credentials=True)
    app.run()
