import datetime
from datetime import timedelta

from django.contrib.sites.shortcuts import get_current_site
from django.db import IntegrityError
from django.db import transaction
from django.http import Http404
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from ics import Calendar
from ics import Event as IcsEvent

from main.forms import CreateMeetupForm
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


def present(request: HttpRequest) -> HttpResponse:
    return render(request, "present.html")


def rules(request: HttpRequest) -> HttpResponse:
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


def create_meetup(request: HttpRequest) -> HttpResponse:
    """Staff-only form to create an Event with 1–3 Presentations in one submit."""
    if not request.user.is_staff:
        raise Http404

    if request.method == "POST":
        form = CreateMeetupForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            slug = slugify(data["title"])
            date_time = timezone.make_aware(
                datetime.datetime.combine(data["date"], data["time"])
            )
            try:
                with transaction.atomic():
                    event = Event.objects.create(
                        title=data["title"],
                        slug=slug,
                        description=data["description"],
                        date_time=date_time,
                        venue=data["venue"],
                    )

                    slots = [
                        (
                            1,
                            data["slot1_name"],
                            data["slot1_presenters"],
                            data.get("slot1_url", ""),
                        ),
                        (
                            2,
                            data.get("slot2_name", ""),
                            data.get("slot2_presenters"),
                            data.get("slot2_url", ""),
                        ),
                        (
                            3,
                            data.get("slot3_name", ""),
                            data.get("slot3_presenters"),
                            data.get("slot3_url", ""),
                        ),
                    ]
                    for order, name, presenter, url in slots:
                        if name:
                            presentation = Presentation.objects.create(
                                name=name,
                                url=url or "",
                                event=event,
                                order=order,
                            )
                            presentation.presenters.add(presenter)

                return redirect(reverse("admin:main_event_change", args=[event.pk]))
            except IntegrityError:
                form.add_error(None, "Υπάρχει ήδη μιτάπ με αυτό το slug.")
    else:
        form = CreateMeetupForm()

    return render(request, "create_meetup.html", {"form": form})
