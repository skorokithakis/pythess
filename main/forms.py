import datetime

from django import forms

from .models import Person
from .models import Venue

_SELECT_CSS = (
    "w-full border border-gray-300 rounded px-3 py-2 "
    "focus:outline-none focus:ring-2 focus:ring-python-blue"
)


class CreateMeetupForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                )
            }
        ),
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 6,
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                ),
            }
        )
    )
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                ),
            }
        )
    )
    time = forms.TimeField(
        widget=forms.TimeInput(
            attrs={
                "type": "time",
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                ),
            }
        ),
        initial=datetime.time(20, 0),
    )
    venue = forms.ModelChoiceField(
        queryset=Venue.objects.order_by("pk"),
        widget=forms.Select(attrs={"class": _SELECT_CSS}),
    )

    # Presentation slot 1 (required)
    slot1_name = forms.CharField(
        max_length=255,
        label="Name",
        widget=forms.TextInput(
            attrs={
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                )
            }
        ),
    )
    slot1_presenters = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=forms.Select(attrs={"class": _SELECT_CSS}),
        label="Presenter",
    )
    slot1_url = forms.URLField(
        required=False,
        label="URL",
        widget=forms.URLInput(
            attrs={
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                )
            }
        ),
    )

    # Presentation slot 2 (optional)
    slot2_name = forms.CharField(
        max_length=255,
        required=False,
        label="Name",
        widget=forms.TextInput(
            attrs={
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                )
            }
        ),
    )
    slot2_presenters = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=forms.Select(attrs={"class": _SELECT_CSS}),
        required=False,
        label="Presenter",
    )
    slot2_url = forms.URLField(
        required=False,
        label="URL",
        widget=forms.URLInput(
            attrs={
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                )
            }
        ),
    )

    # Presentation slot 3 (optional)
    slot3_name = forms.CharField(
        max_length=255,
        required=False,
        label="Name",
        widget=forms.TextInput(
            attrs={
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                )
            }
        ),
    )
    slot3_presenters = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=forms.Select(attrs={"class": _SELECT_CSS}),
        required=False,
        label="Presenter",
    )
    slot3_url = forms.URLField(
        required=False,
        label="URL",
        widget=forms.URLInput(
            attrs={
                "class": (
                    "w-full border border-gray-300 rounded px-3 py-2 "
                    "focus:outline-none focus:ring-2 focus:ring-python-blue"
                )
            }
        ),
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Default venue to the first by pk if not already set.
        if not self.initial.get("venue"):
            first_venue = Venue.objects.order_by("pk").first()
            if first_venue:
                self.initial["venue"] = first_venue.pk

    def clean(self) -> dict:
        cleaned_data = super().clean()

        for slot_number in (2, 3):
            name_key = f"slot{slot_number}_name"
            presenters_key = f"slot{slot_number}_presenters"
            url_key = f"slot{slot_number}_url"
            name_value = cleaned_data.get(name_key)
            presenters_value = cleaned_data.get(presenters_key)
            url_value = cleaned_data.get(url_key)

            slot_has_data = bool(name_value or presenters_value or url_value)

            # If any field in the slot is filled but the name is missing, the
            # slot cannot be saved — name is the primary identifier.
            if slot_has_data and not name_value:
                self.add_error(
                    name_key,
                    "Ο τίτλος είναι υποχρεωτικός όταν συμπληρώνεται οποιοδήποτε άλλο πεδίο της παρουσίασης.",
                )

            # The presenter is required once a name is given.
            if name_value and not presenters_value:
                self.add_error(
                    presenters_key,
                    "Ο ομιλητής είναι υποχρεωτικός όταν συμπληρώνεται τίτλος παρουσίασης.",
                )

        return cleaned_data
