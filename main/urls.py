from django_distill import distill_path

from . import views
from .models import Event


def get_all_events():
    for event in Event.objects.all().order_by("-date_time"):
        yield {"slug": event.slug}


urlpatterns = [
    distill_path("", views.index, name="index"),
    distill_path(
        "meetup/<slug:slug>/", views.meetup, name="meetup", distill_func=get_all_events
    ),
    distill_path("past-meetups/", views.past_meetups, name="past-meetups"),
]
