from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone

from main.models import Event, Person


def past_meetups(request):
    past_events = Event.objects.filter(date_time__lt=timezone.now()).order_by(
        "-date_time"
    )
    return render(request, "past_meetups.html", {"past_meetups": past_events})


def person(request, slug):
    person = get_object_or_404(Person, slug=slug)
    return render(request, "person.html", {"person": person})


def rules(request):
    return render(request, "rules.html")


def index(request):
    future_event = Event.objects.filter(date_time__gt=timezone.now()).first()
    old_events = Event.objects.filter(date_time__lt=timezone.now()).order_by(
        "-date_time"
    )[:3]
    return render(
        request, "index.html", {"future_event": future_event, "old_events": old_events}
    )


def meetup(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, "meetup.html", {"event": event})
