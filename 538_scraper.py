from bs4 import BeautifulSoup
import requests
import re
import json
import csv
import os


def get_latest_approval():
    page = requests.get("https://projects.fivethirtyeight.com/trump-approval-ratings/")

    latest = {}

    soup = BeautifulSoup(page.text, 'html.parser')
    pattern = re.compile(r'var approval=(.*?);')

    all_metas = soup.findAll('meta')
    for meta in all_metas:
        if meta.get("property") == "article:modified_time":
            last_modified = meta.get("content")
            break
    latest["timestamp"] = last_modified

    all_scripts = soup.findAll('script')
    for script in all_scripts:
        result = pattern.search(str(script.string))
        if result:
            raw = result.group(0)

            pattern = re.compile(r"\{(.*?)\}")  # get set of characters in {}
            records = pattern.findall(raw)
            records.reverse()  # as to get most recent last

            for daily_data in records:
                d = json.loads("{" + daily_data + "}")

                if not d['future']:
                    assert(d['subgroup'] == 'All polls')

                    latest['approval'] = float(d['approve_estimate'])
                    latest['disapproval'] = float(d['disapprove_estimate'])
                    break
            break

    latest_poll = {}
    latest_poll_data = soup.findAll('div', {"class": "polls"})[0].table.tbody.find('tr', class_=False)

    latest_poll["date_range"] = latest_poll_data.find('div', {"class", "short"}).string
    latest_poll["pollster"] = latest_poll_data.find('td', {"class", "pollster"}).find('a').string
    latest_poll["link"] = latest_poll_data.find('td', {"class", "pollster"}).find('a')["href"]
    latest_poll["approval"] = latest_poll_data.find('td', {"class", "first"}).find('div', {"class", "heat-map"}).string
    latest_poll["disapproval"] = latest_poll_data.find('td', {"class", "last"}).find('div', {"class", "heat-map"}).string
    latest_poll["adj_approval"] = latest_poll_data.find('td', {"class", "answer adjusted first"}).find('div', {"class", "heat-map"}).string
    latest_poll["adj_disapproval"] = latest_poll_data.find('td', {"class", "answer adjusted last"}).find('div', {"class", "heat-map"}).string

    return latest, latest_poll

def update_data(dest="538data/"):
    agg, curr = get_latest_approval()

    if not os.path.exists(dest):
        os.makedirs(dest)

    new = False

    if not os.path.exists(dest + "meta.csv"):
        new = True
        with open(dest + "meta.csv", "a") as meta_file:
            meta_writer = csv.writer(meta_file)
            meta_writer.writerow([agg['timestamp']])
        meta_file.close()


    with open(dest + "meta.csv", "r") as meta_file:
        meta_reader = csv.reader(meta_file)
        timestamp = next(meta_reader)[0]

        update = ((timestamp != agg['timestamp']) or new)
    meta_file.close()

    if update:
        with open(dest + "aggregate.csv", "w") as agg_file:
            agg_writer = csv.writer(agg_file, delimiter=",")
            agg_writer.writerow([agg['timestamp'], agg['approval'], agg['disapproval']])
        agg_file.close()

        with open(dest + "polls.csv", "w") as polls_file:
            polls_writer = csv.writer(polls_file, delimiter=",")
            polls_writer.writerow([curr['date_range'], curr['pollster'], curr['link'], curr['approval'], curr['disapproval'], curr['adj_approval'], curr['adj_disapproval']])
        polls_file.close()


update_data()