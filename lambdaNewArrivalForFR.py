import os
import requests
from bs4 import BeautifulSoup
import json
import boto3

target_url = os.environ["TARGET_URL"]
slack_url = os.environ["SLACK_URL"]


def handler(event, context):
    dynamoDB = boto3.resource("dynamodb")
    table = dynamoDB.Table("new_arrival_for_fr")

    result = table.scan()
    realty_list_old = [item.get("realty") for item in result["Items"]]

    realty_list_new = []

    message = ""
    req = requests.get(target_url)
    soup = BeautifulSoup(req.text.encode("utf-8"), "html.parser")

    for bukken_list in soup.find_all("td", class_="td_bukken_data"):
        bukken_info = ""
        for bukken in bukken_list.find_all("td", class_="td_data_value"):
            bukken_info += bukken.get_text() + " "
        realty_list_new.append(bukken_info.strip())

    old_set = set(realty_list_old)
    new_set = set(realty_list_new)
    unmatched_list = list(new_set.difference(old_set))

    for s in unmatched_list:
        message += s + "\n"

    if message != "":
        message = "不動産連合隊\n" + message
        post(message)
    
    truncate_dynamo_items(table)

    with table.batch_writer() as batch:
        for realty in realty_list_new:
            batch.put_item(Item={"realty": realty})


def post(message):
    values = {
        "text": message,
        "username": "bot"
    }
    requests.post(slack_url, data=json.dumps(values))


def truncate_dynamo_items(dynamodb_table):

    # データ全件取得
    delete_items = []
    parameters = {}
    while True:
        response = dynamodb_table.scan(**parameters)
        delete_items.extend(response["Items"])
        if ("LastEvaluatedKey" in response):
            parameters["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        else:
            break

    # キー抽出
    key_names = [x["AttributeName"] for x in dynamodb_table.key_schema]
    delete_keys = [{k: v for k, v in x.items() if k in key_names}
                   for x in delete_items]

    # データ削除
    with dynamodb_table.batch_writer() as batch:
        for key in delete_keys:
            batch.delete_item(Key=key)
