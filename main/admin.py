from django.contrib import admin

# Register your models here.
from .models import Venue, Person, Presentation, Event


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address_url")
    search_fields = ("name",)


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    search_fields = ("name",)


@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    search_fields = ("name",)
    filter_horizontal = ("presenters",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ["title"]}
    list_display = ("title", "slug", "date_time", "venue")
    list_filter = ("date_time", "venue")
    search_fields = ("title", "description")