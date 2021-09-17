import datetime
import time

def getTimeByIndex(index):
    return datetime.date.fromtimestamp(1577980800) + datetime.timedelta(days = index)

def getTimestampByStr(str):
    return time.mktime(time.strptime(str[:19], "%Y-%m-%dT%H:%M:%S"))

def readFile(path):
    file = open("cache/data.json")
    return file.read()

def saveFile(path, context):
    with open(path, 'w', encoding='utf-8') as file:
        file.write(context)
