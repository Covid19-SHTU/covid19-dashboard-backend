import datetime
import time

def getTimeByIndex(index):
    return (datetime.datetime(2020, 1, 3, 0, 0, 0) + datetime.timedelta(days = index)).replace(tzinfo = datetime.timezone.utc).timestamp()

def getTimestampByStr(str):
    return time.mktime(time.strptime(str[:19], "%Y-%m-%dT%H:%M:%S"))

def getTimeNow():
    return time.time()
