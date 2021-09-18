import orjson
import requests
import os
import countryinfo
import functions
from flask import Flask
from flask import jsonify
from flask_caching import Cache

world = {}
country = {}
update = 4102329600.0
cache = 3600
latest = functions.getTimestampByStr(orjson.loads(requests.get("https://covid19.who.int/page-data/sq/d/361700019.json").text)["data"]["lastUpdate"]["date"])

for item in countryinfo.country_list:
    country[item] = {}

if not os.path.exists("cache"):
     os.makedirs("cache")

if os.path.exists("cache/update.txt"):
    file = open("cache/update.txt")
    update = float(file.read())
    file.close()

if not os.path.exists("cache/data.json") or latest > update:
    url = "https://covid19.who.int/page-data/measures/page-data.json"
    request = requests.get(url)
    with open('cache/data.json', 'w', encoding='utf-8') as file:
        file.write(request.text)

file = open("cache/data.json")
data = orjson.loads(file.read())["result"]["pageContext"]["rawDataSets"]
file.close()

with open('cache/update.txt', 'w', encoding='utf-8') as file:
    file.write(str(functions.getTimestampByStr(data["lastUpdate"])))

for item in data["countriesCurrent"]["rows"]:
    if item[0] in country:
        country[item[0]]["deaths"] = item[1]
        country[item[0]]["cumulative_deaths"] = item[2]
        country[item[0]]["cases"] = item[6]
        country[item[0]]["cumulative_cases"] = item[7]

for item in data["vaccineData"]["data"]:
    key = countryinfo.get_iso(item["ISO3"])
    if key in country:
        country[key]["total_vaccinated"] = item["TOTAL_VACCINATIONS"]
        country[key]["1plus_vaccinated"] = item["PERSONS_VACCINATED_1PLUS_DOSE"]
        country[key]["fully_vaccinated"] = item["PERSONS_FULLY_VACCINATED"]

for item in data["countryGroups"]:
    if item["value"] in country:
        country[item["value"]]["history"] = []
        for index, row in enumerate(item["data"]["rows"]):
            country[item["value"]]["history"].append({
                "time": functions.getTimeByIndex(index),
                "deaths": row[2],
                "cumulative_deaths": row[3],
                "cases": row[7],
                "cumulative_cases": row[8]
            })

world["deaths"] = data["today"]["Deaths"]
world["cumulative_deaths"] = data["today"]["Cumulative Deaths"]
world["cases"] = data["today"]["Confirmed"]
world["cumulative_cases"] = data["today"]["Cumulative Confirmed"]

result = {
    "world": world,
    "country": country
}

app = Flask(__name__)
app.config.from_mapping({"CACHE_TYPE": "SimpleCache"})
cache = Cache(app)

@app.route('/')
@cache.cached(timeout = 3600)
def index():
    return jsonify(result)

if __name__ == '__main__':
    app.run()
