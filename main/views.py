from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from main.models import Event


# Create your views here.
def index(request):
    future_event = Event.objects.filter(date_time__gt=timezone.now()).first()
    old_events = Event.objects.filter(date_time__lt=timezone.now()).order_by(
        "-date_time"
    )
    return render(
        request, "index.html", {"future_event": future_event, "old_events": old_events}
    )


def meetup(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, "meetup.html", {"event": event})