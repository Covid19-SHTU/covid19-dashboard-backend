
# 后端 API 文档

## 约定

* API 一律返回 json 格式数据
* response 中必有一项“status”，值为 200 表示返回结果正常，其他值表示存在异常
  * 若存在异常则有一项 "error_msg"，表示对异常的描述

## GET /

返回首页信息

## GET /country/\<string:country_name\>

返回代号为 `country_name` 的国家的数据

例： `GET /country/CN`

