from datetime import timedelta

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from ics import Calendar
from ics import Event as IcsEvent

from main.models import Event
from main.models import Person
from main.models import Presentation


def headers(request):
    """Generate the required headers for Cloudflare Pages."""
    lines = []
    # We're only doing future events because CF Pages has a 100 rule limit, and people
    # probably don't need to add old events to their calendars. If they do, they need to
    # sort their life out.
    for event in Event.objects.filter(date_time__gt=timezone.now()):
        lines.append(
            f"{reverse('meetup-ics', args=[event.slug])}\n  Content-Type: text/calendar"
        )

    return HttpResponse("\n\n".join(lines))


def past_meetups(request):
    past_events = Event.objects.filter(date_time__lt=timezone.now()).order_by(
        "-date_time"
    )
    return render(request, "past_meetups.html", {"past_meetups": past_events})


def person(request, slug):
    person = get_object_or_404(Person, slug=slug)
    return render(request, "person.html", {"person": person})


def people(request):
    people = Person.objects.all().order_by("name")
    return render(request, "people.html", {"people": people})


def presentations(request):
    presentations = Presentation.objects.all().order_by("name")
    return render(request, "presentations.html", {"presentations": presentations})


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


def meetup_ics(request, slug):
    event = get_object_or_404(Event, slug=slug)
    calendar = Calendar()
    cal_event = IcsEvent()
    cal_event.name = f"PyThess - {event.title}"
    cal_event.description = event.description
    cal_event.location = f"{event.venue.name} ({event.venue.address_url})"
    cal_event.url = (
        f"https://{get_current_site(request).domain}{event.get_absolute_url()}"
    )
    cal_event.begin = event.date_time
    cal_event.end = event.date_time + timedelta(hours=6)
    calendar.events.add(cal_event)

    response = HttpResponse(calendar.serialize(), content_type="text/calendar")
    response["Content-Disposition"] = f'attachment; filename="{slug}.ics"'
    return response


def page_not_found(request):
    return render(request, "404.html")


def splash(request):
    """Full-screen splash page with QR codes for meetup start."""
    qr_items = [
        {
            "url": "https://www.pythess.org",
            "icon": "fa-brands fa-python",
            "color": "#ffcc3b",
        },
        {
            "url": "https://discord.gg/U9bRsHfvBy",
            "icon": "fa-brands fa-discord",
            "color": "#5865F2",
        },
        # {
        #    "url": "https://www.meetup.com/pythess/",
        #    "icon": "fa-brands fa-meetup",
        #    "color": "#ED1C40",
        # },
    ]
    return render(request, "splash.html", {"qr_items": qr_items})
