#!/usr/bin/env python
import os
import sys

from urlify import urlify

# Add the project root to the path
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

import django

# Set the Django settings module and initialize Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pythess.settings")
django.setup()

import json

from pydantic import BaseModel, Field
from datetime import datetime
from main.models import Event


class Meetup(BaseModel):
    title: str
    slug: str
    description: str
    date_time: datetime = Field(..., alias="dateTime")
    event_url: str = Field(..., alias="eventUrl")
    id: str
    venue: dict

    class Config:
        # Allow population using field names even if aliases are provided.
        allow_population_by_field_name = True


def add_meetup(meetup: Meetup):
    if Event.objects.filter(slug=meetup.slug).exists():
        print(f"Meetup {meetup.slug} already exists, continuing...")
        return
    venue_ids = {
        "Allegro": 5,
        "Cafe del Arte, Βασιλικό θέατρο": 7,
        "Coho": 1,
        "Make Creative Spaces (make.gr)": 3,
        "OK!Thess": 4,
        "OKThess": 4,
        "Ελιά Λεμόνι": 6,
        "Τηγανιές και Σχάρες": 2,
    }
    event = Event()
    event.title = meetup.title
    event.meetup_com_id = meetup.id
    event.slug = meetup.slug
    event.description = meetup.description
    event.date_time = meetup.date_time
    event.venue_id = venue_ids[meetup.venue["name"]]
    event.save()


def main():
    with open("misc/meetups.json", "r") as infile:
        meetups = json.load(infile)

    for item in meetups:
        events = item["data"]["groupByUrlname"]["events"]["edges"]
        if not events:
            continue
        for event in events:
            meetup_data = event["node"]
            meetup = Meetup(**meetup_data, slug=urlify(meetup_data["title"]))
            add_meetup(meetup)


if __name__ == "__main__":
    main()
