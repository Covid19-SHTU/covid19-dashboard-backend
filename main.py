import orjson
import requests
import os
import countryiso

country = ['AF', 'AL', 'DZ', 'AS', 'AD', 'AO', 'AI', 'AG', 'AR', 'AM', 'AW', 'AU', 'AT', 'AZ', 'BS', 'BH', 'BD', 'BB', 'BY', 'BE', 'BZ', 'BJ', 'BM', 'BT', 'BO', 'BA', 'BW', 'BR', 'VG', 'BN', 'BG', 'BF', 'CV', 'KH', 'CM', 'CA', 'KY', 'CF', 'TD', 'CL', 'CN', 'CO', 'KM', 'CG', 'CK', 'CR', 'CI', 'HR', 'CU', 'CY', 'CZ', 'CD', 'DK', 'DJ', 'DM', 'DO', 'EC', 'EG', 'SV', 'GQ', 'EE', 'SZ', 'ET', 'FK', 'FO', 'FJ', 'FI', 'FR', 'GF', 'PF', 'GA', 'GM', 'GE', 'DE', 'GH', 'GI', 'GR', 'GL', 'GD', 'GP', 'GU', 'GT', 'GG', 'GN', 'GW', 'GY', 'HT', 'HN', 'IS', 'IN', 'ID', 'IR', 'IQ', 'IE', 'IM', 'IL', 'IT', 'JM', 'JP', 'JE', 'JO', 'KZ', 'KE', 'KI', 'XK', 'KW', 'KG', 'LA', 'LV', 'LB', 'LS', 'LR', 'LY', 'LI', 'LT', 'LU', 'MG', 'MW', 'MY', 'MV', 'ML', 'MT', 'MH', 'MQ', 'MR', 'MU', 'MX', 'FM', 'MC', 'MN', 'ME', 'MS', 'MA', 'MZ', 'MM', 'NA', 'NR', 'NP', 'NL', 'NC', 'NZ', 'NI', 'NE', 'NG', 'NU', 'MK', 'MP', 'NO', 'PS', 'OM', 'PK', 'PW', 'PA', 'PG', 'PY', 'PE', 'PH', 'PN', 'PL', 'PT', 'PR', 'QA', 'KR', 'MD', 'RO', 'RU', 'RW', 'SH', 'KN', 'LC', 'VC', 'WS', 'SM', 'ST', 'SA', 'SN', 'RS', 'SC', 'SL', 'SG', 'SK', 'SI', 'SB', 'SO', 'ZA', 'SS', 'ES', 'LK', 'SD', 'SR', 'SE', 'CH', 'SY', 'TJ', 'TH', 'GB', 'TL', 'TG', 'TK', 'TO', 'TT', 'TN', 'TR', 'TM', 'TC', 'TV', 'UG', 'UA', 'AE', 'TZ', 'US', 'UY', 'VU', 'VE', 'VN', 'WF', 'YE', 'ZM', 'ZW']

result = {}

for item in country:
    result[item] = {}

if not os.path.exists("cache"):
     os.makedirs("cache")

if not os.path.exists("cache/data.json"):
    url = "https://covid19.who.int/page-data/measures/page-data.json"
    request = requests.get(url)
    with open('cache/data.json', 'w', encoding='utf-8') as file:
        file.write(request.text)

file = open("cache/data.json")
data = orjson.loads(file.read())["result"]["pageContext"]["rawDataSets"]

vaccine = data["vaccineData"]["data"]
for item in data["countriesCurrent"]["rows"]:
    if item[0] in result:
        result[item[0]]["deaths"] = item[1]
        result[item[0]]["cumulative_deaths"] = item[2]
        result[item[0]]["cases"] = item[6]
        result[item[0]]["cumulative_cases"] = item[7]

for item in vaccine:
    key = countryiso.getISO2(item["ISO3"])
    if key in result:
        result[key]["total_vaccinated"] = item["TOTAL_VACCINATIONS"]
        result[key]["1plus_vaccinated"] = item["PERSONS_VACCINATED_1PLUS_DOSE"]
        result[key]["fully_vaccinated"] = item["PERSONS_FULLY_VACCINATED"]

for item in data["countryGroups"]:
    if item["value"] in result:
        result[item["value"]]["history"] = []
        for row in item["data"]["rows"]:
            result[item["value"]]["history"].append({
                "deaths": row[2],
                "cumulative_deaths": row[3],
                "cases": row[7],
                "cumulative_cases": row[8]
            })

for key, item in result.items():
    if key == "US":
        print(item)
