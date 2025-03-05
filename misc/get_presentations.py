#!/usr/bin/env python3
import json
import os
import sys

import anthropic
import django

current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)


# Set the Django settings module and initialize Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pythess.settings")
django.setup()

from main.models import Event  # noqa


def get_presentations(description: str):
    client = anthropic.Anthropic()
    prompt = (
        "I have the description (in Greek) for my meetup, PyThess. The description"
        " contains the titles of the presentations and names of the presenters, "
        "sometimes in a facetious, tongue-in-cheek format. My name is Σταύρος "
        "Κοροκυθάκης, so whenever the text refers to 'me', use my name in your output."
        " Please return the titles of the presentations, as close as you can get them "
        "(in the original language), and the names of the presenters for each. "
        "If the text is being funny and cryptic about the title, make the returned title"
        " as close to the text as you can, to keep it funny.\n"
        "Output JSON, a list of [[title, [presenter1, presenter2]], ]. "
        "Output JUST the JSON, no Markdown. "
        "Here is the event description:\n\n" + description
    )
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=4000,
        temperature=0,
        system="You are a helpful assistant, deriving presentation titles and names from text.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt,
                    }
                ],
            }
        ],
    )
    return message.content


def main():
    for event in Event.objects.filter(presentations__isnull=True):
        print(event.description)
        r = get_presentations(event.description)
        text = r[0].text
        print(event.title)
        print(json.loads(text))
        input()


if __name__ == "__main__":
    main()
