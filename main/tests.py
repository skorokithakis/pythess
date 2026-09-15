import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Event
from main.models import Person
from main.models import Venue


class CreateMeetupViewTests(TestCase):
    def setUp(self) -> None:
        self.staff_user = User.objects.create_superuser(
            username="staff", password="password", email="staff@example.com"
        )
        self.client.force_login(self.staff_user)
        self.venue = Venue.objects.create(
            name="Venue", address_url="https://example.com"
        )
        self.presenter = Person.objects.create(
            name="Presenter", slug="presenter", gender="male"
        )
        self.valid_data = {
            "title": "Θεσσαλονίκη",
            "slug": "thessaloniki",
            "description": "Description",
            "date": "2030-01-01",
            "time": "20:00",
            "venue": self.venue.pk,
            "slot1_name": "Talk",
            "slot1_presenters": self.presenter.pk,
            "slot1_url": "",
        }

    def test_greek_title_creates_event_at_posted_slug(self) -> None:
        response = self.client.post(reverse("create-meetup"), self.valid_data)

        event = Event.objects.get(title="Θεσσαλονίκη")
        self.assertEqual(event.slug, "thessaloniki")
        self.assertRedirects(
            response, reverse("admin:main_event_change", args=[event.pk])
        )

        meetup_response = self.client.get(reverse("meetup", args=["thessaloniki"]))
        self.assertEqual(meetup_response.status_code, 200)

    def test_duplicate_slug_reports_error_on_slug_field_and_keeps_values(self) -> None:
        Event.objects.create(
            title="Existing",
            slug="thessaloniki",
            description="Description",
            date_time=timezone.make_aware(datetime.datetime(2030, 1, 1, 20, 0)),
            venue=self.venue,
        )

        response = self.client.post(reverse("create-meetup"), self.valid_data)

        form = response.context["form"]
        self.assertIn("slug", form.errors)
        self.assertNotIn("__all__", form.errors)
        self.assertEqual(form.data["title"], "Θεσσαλονίκη")
        self.assertEqual(Event.objects.count(), 1)
