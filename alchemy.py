import copy
import sys

import orjson
import requests
import os
import countryinfo
import functions
from mytensorflow import *


debug_mode = 'DEBUG_MODE' in os.environ

# Data of the epidemic
world = {}
country = {}

# The last update time of our backend
update = 4102329600.0

# The timestamp of the latest version of the data
#latest = functions.getTimestampByStr(orjson.loads(requests.get("https://covid19.who.int/page-data/sq/d/464037013.json").text)["data"]["lastUpdate"]["date"])
latest=0

# Data of the vaccination = 0
total_vaccinated = 0
plus_vaccinated = 0
fully_vaccinated = 0

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
                "time": functions.getTimeByIndex(index),
                "deaths": row[2],
                "cumulative_deaths": row[3],
                "cases": row[7],
                "cumulative_cases": row[8]
            })

world["history"] = {}
world["history"]["daily"] = []
world["history"]["cumulative"] = []

for index, row in enumerate(data["byDay"]["rows"]):
    world["history"]["daily"].append({
        "time": functions.getTimeByIndex(index),
        "deaths": row[1],
        "cases": row[6],
    })

for index, row in enumerate(data["byDayCumulative"]["rows"]):
    world["history"]["cumulative"].append({
        "time": functions.getTimeByIndex(index),
        "deaths": row[1],
        "cases": row[6],
    })

world["update"] = functions.getTimestampByStr(data["lastUpdate"])
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







if __name__ == '__main__':
    print("main!")
    total=len(result['country'])
    cnt=0
    for i in result['country']:
        cnt+=1
        print("total:",total,"now",cnt)
        b = []
        for j in result['country'][i]['history']:
            b.append(j['cases'])
        tensorflow_alchemy(b, 7, i+"_c")
        b = []
        for j in result['country'][i]['history']:
            b.append(j['deaths'])
        tensorflow_alchemy(b, 7, i+"_d")

