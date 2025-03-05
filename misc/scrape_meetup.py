#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "requests",
#     "pudb",
# ]
# ///
import json
import re
import sys
from pprint import pprint

import requests


def main(end_cursor=None):
    url = "https://www.meetup.com/gql2"

    headers = {"cookie": sys.argv[1]}

    payload = {
        "operationName": "getPastGroupEvents",
        "variables": {
            "urlname": "pythess",
            "beforeDateTime": "2125-03-05T09:40:14.711Z",
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "eb05e53c448e9ec22c069e5d1ed091781eff823911bf6b46d548a295b1a7502a",
            }
        },
    }
    if end_cursor:
        payload["variables"]["after"] = end_cursor

    response = requests.post(url, json=payload, headers=headers)
    return response.json()


if __name__ == "__main__":
    end_cursor = None
    meetups = []
    while True:
        j = main(end_cursor)
        if not j:
            break
        meetups.append(j)
        titles = re.findall(r"'title': '(.*?)'", repr(j))
        print(titles)
        if not titles:
            break
        end_cursor = j["data"]["groupByUrlname"]["events"]["pageInfo"]["endCursor"]

    with open("meetups.json", "w") as f:
        json.dump(meetups, f, indent=2, sort_keys=True)
