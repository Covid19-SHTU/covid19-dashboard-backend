import datetime
import time

def getTimeByIndex(index):
    return datetime.date(2020, 1, 3) + datetime.timedelta(days = index)

def getTimestampByStr(str):
    return time.mktime(time.strptime(str[:19], "%Y-%m-%dT%H:%M:%S"))
