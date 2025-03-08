from django.contrib import admin

from .models import Event
from .models import Person
from .models import Presentation
from .models import Venue

# Register your models here.


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address_url")
    search_fields = ("name",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["name"]}
    list_display = ("name", "slug", "url")
    search_fields = ("name",)


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "event", "order")
    ordering = ["event", "order"]
    search_fields = ("name",)
    filter_horizontal = ("presenters",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["title"]}
    list_display = ("title", "slug", "date_time", "venue")
    list_filter = ("date_time", "venue")
    search_fields = ("title", "description")
