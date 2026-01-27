"""Meetup.com API integration for publishing events."""
import requests
from django.utils import timezone

from main.models import Event

# Constants for Meetup.com event creation
GROUP_URLNAME = "pythess"
VENUE_ID = "25294885"
FEATURED_PHOTO_ID = 524708401
DURATION = "PT5H"
HOW_TO_FIND_US = "Θα είμαστε στην υπόγα, μπείτε από την πλαϊνή πόρτα (δεξιά) του κόχο."

# GraphQL mutation for creating a Meetup event
CREATE_EVENT_MUTATION = """
mutation($input: CreateEventInput!) {
  createEvent(input: $input) {
    event {
      id
    }
    errors {
      message
      code
      field
    }
  }
}
"""


def publish_event_to_meetup(event: Event, token: str) -> str:
    """
    Publish a Django Event instance to Meetup.com as a draft event.

    Args:
        event: The Event instance to publish
        token: Meetup.com API bearer token

    Returns:
        The Meetup event ID

    Raises:
        Exception: If the API returns errors or the request fails
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Convert to local timezone before formatting, since Meetup expects local time
    # but Django stores datetimes in UTC.
    local_date_time = timezone.localtime(event.date_time)
    start_date_time = local_date_time.strftime("%Y-%m-%dT%H:%M")

    payload = {
        "query": CREATE_EVENT_MUTATION,
        "variables": {
            "input": {
                "groupUrlname": GROUP_URLNAME,
                "title": event.title,
                "description": event.description,
                "startDateTime": start_date_time,
                "venueId": VENUE_ID,
                "featuredPhotoId": FEATURED_PHOTO_ID,
                "duration": DURATION,
                "howToFindUs": HOW_TO_FIND_US,
                "publishStatus": "DRAFT",
                "feeOption": {
                    "amount": 200,
                    "currency": "EUR",
                    "paymentMethod": "CASH",
                    "refundPolicy": "Άμα θέλετε επιστροφή χρημάτων να μου δώσετε πίσω τις δύο ώρες που έφαγα να σας οργανώνω.",
                },
                "rsvpSettings": {
                    "guestLimit": 5,
                    "rsvpOpenDuration": "PT0S",
                    "rsvpCloseDuration": "PT0S",
                    "rsvpLimit": 0,
                },
            }
        },
    }

    response = requests.post(
        "https://api.meetup.com/gql-ext",
        headers=headers,
        json=payload,
        timeout=30,
    )

    # Raise an exception if the HTTP request failed.
    response.raise_for_status()

    response_data = response.json()

    # Check for GraphQL errors in the response.
    if "errors" in response_data:
        error_messages = [error["message"] for error in response_data["errors"]]
        raise Exception(f"GraphQL errors: {', '.join(error_messages)}")

    # Check for mutation-specific errors.
    create_event_data = response_data.get("data", {}).get("createEvent", {})
    if create_event_data.get("errors"):
        error_messages = [
            f"{error['field']}: {error['message']}"
            for error in create_event_data["errors"]
        ]
        raise Exception(f"Meetup API errors: {', '.join(error_messages)}")

    # Extract and return the event ID.
    event_data = create_event_data.get("event")
    if not event_data:
        raise Exception("No event ID returned from Meetup API")

    event_id = event_data.get("id")
    if not event_id:
        raise Exception("No event ID returned from Meetup API")

    return event_id
