from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import path
from django.urls import reverse

from .meetup import publish_event_to_meetup
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

    class Media:
        css = {"all": ["admin/event_admin.css"]}

    def get_urls(self):
        """Add custom URL for publishing event to Meetup."""
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/publish-to-meetup/",
                self.admin_site.admin_view(self.publish_to_meetup_view),
                name="main_event_publish_to_meetup",
            ),
        ]
        return custom_urls + urls

    def publish_to_meetup_view(self, request, object_id):
        """Handle publishing an event to Meetup.com."""
        event = get_object_or_404(Event, pk=object_id)

        # Check if event is already published to Meetup.
        if event.meetup_com_id:
            messages.error(
                request,
                f"Event '{event.title}' is already published to Meetup (ID: {event.meetup_com_id}).",
            )
            return redirect(reverse("admin:main_event_change", args=[event.pk]))

        try:
            # Publish the event to Meetup and get the ID.
            meetup_id = publish_event_to_meetup(event, settings.MEETUP_TOKEN)

            # Save the Meetup ID to the event.
            event.meetup_com_id = meetup_id
            event.save()

            messages.success(
                request,
                f"Event '{event.title}' successfully published to Meetup (ID: {meetup_id}).",
            )
        except Exception as e:
            messages.error(
                request,
                f"Failed to publish event to Meetup: {str(e)}",
            )

        return redirect(reverse("admin:main_event_change", args=[event.pk]))

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Add context to show/hide the Publish to Meetup button."""
        extra_context = extra_context or {}

        if object_id:
            event = get_object_or_404(Event, pk=object_id)
            extra_context["show_publish_to_meetup"] = not event.meetup_com_id

        return super().change_view(
            request, object_id, form_url, extra_context=extra_context
        )
