import os
import requests
from bs4 import BeautifulSoup
import json
import time
import codecs
from dotenv import load_dotenv

target_url = os.environ["TARGET_URL"]
slack_url = os.environ["SLACK_URL"]
realty_list_file = "./list/FudousanRengoutaiList.txt"

def main():
    i = 0
    realty_list_old = []
    if os.path.exists(realty_list_file):
        with codecs.open(realty_list_file, "r", "utf-8") as f:
            for line in f:
                realty_list_old.append(line.strip())

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

    realty_list_old = list(realty_list_new)

    with codecs.open(realty_list_file, "w", "utf-8") as f:
        for text in realty_list_new:
            f.write(text + "\n")

def post(message):
    values = {
        "text": message,
        "username": "bot"
    }
    requests.post(slack_url, data=json.dumps(values))


if __name__ == "__main__":
    load_dotenv()
    main()
