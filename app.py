import orjson
import requests
import os
import countryiso
import functions
from flask import Flask
from flask import jsonify

country_list = ['AF', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ', 'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BA', 'BW', 'BR', 'VG', 'BN', 'BG', 'BF', 'CV', 'KH', 'CM', 'CA', 'KY', 'CF', 'TD', 'CL', 'CN', 'CO', 'KM', 'CG', 'CK', 'CR', 'CI', 'HR', 'CU', 'CY', 'CZ', 'CD', 'DK', 'DJ', 'DM', 'DO', 'EC', 'EG', 'SV', 'GQ', 'EE', 'SZ', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF', 'GA', 'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN', 'GW', 'GY', 'HT', 'HN', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IL', 'IT', 'JM', 'JP', 'JE', 'JO', 'KZ', 'KE', 'KI', 'XK', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'MX', 'FM', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'MK', 'MP', 'NO', 'PS', 'OM', 'PK', 'PW', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN', 'PL', 'PT', 'PR', 'QA', 'KR', 'MD', 'RO', 'RU', 'RW', 'SH', 'KN', 'LC', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 'SC', 'SL', 'SG', 'SK', 'SI', 'SB', 'SO', 'ZA', 'SS', 'ES', 'LK', 'SD', 'SR', 'SE', 'CH', 'SY', 'TJ', 'TH', 'GB', 'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UG', 'UA', 'AE', 'TZ', 'US', 'UY', 'VU', 'VE', 'VN', 'WF', 'YE', 'ZM', 'ZW']

world = {}
country = {}
update = 4102329600.0
latest = functions.getTimestampByStr(orjson.loads(requests.get("https://covid19.who.int/page-data/sq/d/361700019.json").text)["data"]["lastUpdate"]["date"])

for item in country_list:
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
    key = countryiso.getISO2(item["ISO3"])
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

@app.route('/')
def index():
    return jsonify(result)

if __name__ == '__main__':
    app.run()


