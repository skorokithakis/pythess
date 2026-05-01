---
id: pyt-lsilx
status: closed
deps: []
links: []
created: 2026-05-01T23:34:23Z
type: task
priority: 2
assignee: Stavros Korokithakis
---
# Create-meetup form for staff

Add a staff-only page at /create-meetup/ that creates an Event plus 1–3 Presentations in one submit, plus a navbar link visible only to staff.

Form fields:
- Event: title (required), description (required, plain textarea — rendered as markdown elsewhere via the markdownify filter), date (required), time (required, default 20:00), venue (Select of existing Venues, defaults to first by id).
- Slug: auto-generate from title via django.utils.text.slugify; on collision, return form error 'A meetup with this slug already exists' (no auto-suffixing). Mirror the admin's behaviour: do not expose the slug field in the form.
- Presentation slots 1–3: name, presenters (multi-select of existing Person, required if slot is filled), url (optional). Slot 1 is required. A slot is considered filled iff its name is non-empty; in that case presenters becomes required for that slot. Slots 2 and 3 may be left fully blank.
- order on each saved Presentation = slot index (1, 2, 3).

Behaviour:
- Wrap the create in transaction.atomic; on validation failure nothing is saved.
- On success redirect to the admin event change page (reverse('admin:main_event_change', args=[event.pk])).
- Access control: gate by request.user.is_staff. Non-staff get Http404 (use a decorator-style check; do NOT redirect to login — the page should be invisible to non-staff). Anonymous users also 404.
- URL: regular path() (NOT distill_path) in main/urls.py. Do not add it to the static export.
- Navbar link 'Create meetup' visible only when request.user.is_staff. Place in templates/base.html (check existing navbar structure first).
- Next to the venue select and each presenters select, add small links 'add new' opening /admin/main/venue/add/ and /admin/main/person/add/ in a new tab.

Client-side autosave (vanilla JS, inline in the template is fine):
- On any input/change in the form, serialize all event + presentation field values to localStorage under a single key (e.g. 'createMeetupDraft').
- On page load, if the key exists, restore values into the form fields before the user interacts.
- On successful submit, clear the key. Easiest reliable approach: clear it from the server-rendered success page (it redirects to admin, so instead clear it on form submit just before navigation, OR set a flag in sessionStorage / use the fact that a fresh GET to /create-meetup/ with no draft expected is the next-time scenario — pick whichever is cleanest). Multi-select values must round-trip correctly.

Form implementation:
- Single django.forms.Form subclass is fine (not ModelForm) — the form spans Event + 3 Presentations and has slot logic. Keep it in main/forms.py (new file).

Non-goals:
- No inline creation of Person or Venue.
- No editing of existing meetups.
- No tests for this view.
- No file uploads, rich text editor, or presenter ordering UI.
- No markdown preview (separate ticket).

Caveats:
- The site is partly statically generated via django-distill; this view is dynamic-only and intentionally not part of the static export.
- Description is stored as plain text in TextField; meetup.html uses {{ event.description|markdownify }}, so admins write markdown.
- Existing admin uses prepopulated_fields={'slug': ['title']} for events; this form mimics that server-side via slugify.
- existing Venue ordering has no Meta.ordering; default to first by pk.

## Acceptance Criteria

Logged-in staff member visiting /create-meetup/ can create a meetup with 1, 2, or 3 presentations and is redirected to the admin event change view; the new Event and Presentations exist with correct order values and presenter M2M links. Non-staff (anonymous or non-staff users) get 404 at the URL and do not see the navbar link. Validation errors (e.g. missing required field, slug collision, presenters missing on a filled slot) re-render the form with all values preserved and no DB writes. Refreshing the form page after typing some values restores them from localStorage.

