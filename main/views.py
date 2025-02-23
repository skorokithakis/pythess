from django.shortcuts import render
from main.models import Event
from django.utils import timezone


# Create your views here.
def index(request):
    future_event = Event.objects.filter(date_time__gt=timezone.now()).first()
    old_events = Event.objects.filter(date_time__lt=timezone.now()).order_by("-date_time")
    return render(request, "index.html", {"future_event": future_event, "old_events": old_events})
