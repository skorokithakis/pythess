from django_distill import distill_path

from . import views
from .models import Event
from .models import Person


def get_all_events():
    for event in Event.objects.all().order_by("-date_time"):
        yield {"slug": event.slug}


def get_all_people():
    for person in Person.objects.all().order_by("name"):
        yield {"slug": person.slug}


urlpatterns = [
    distill_path("", views.index, name="index"),
    distill_path("presentations/", views.presentations, name="presentations"),
    distill_path("_headers", views.headers, name="headers"),
    distill_path("people/", views.people, name="people"),
    distill_path(
        "person/<slug:slug>/", views.person, name="person", distill_func=get_all_people
    ),
    distill_path(
        "meetup/<slug:slug>/", views.meetup, name="meetup", distill_func=get_all_events
    ),
    distill_path(
        "meetup/<slug:slug>/ics/",
        views.meetup_ics,
        name="meetup-ics",
        distill_func=get_all_events,
    ),
    distill_path("past-meetups/", views.past_meetups, name="past-meetups"),
    distill_path("rules/", views.rules, name="rules"),
]
