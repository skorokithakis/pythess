from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from .models import Event


class LatestMeetupsFeed(Feed):
    title = "Τα μιτάπ του PyThess"
    link = reverse_lazy("meetup-feed")
    description = "Τα τελευταία μιτάπ του PyThess"

    def items(self):
        return Event.objects.all()[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return item.date_time
