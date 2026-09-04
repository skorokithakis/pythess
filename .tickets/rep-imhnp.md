---
id: rep-imhnp
status: closed
deps: []
links: []
created: 2026-09-04T20:45:09Z
type: task
priority: 2
assignee: Stavros Korokithakis
---
# Contest overlay: templates/contest.html included from base.html

Objective: A ridiculous "ΜΕΓΑΛΟΣ ΔΙΑΓΩΝΙΣΜΟΣ" full-screen overlay on every page, shown ~2s after load, once per browser session.

Files: new templates/contest.html (all markup, CSS, JS self-contained); one {% include "contest.html" %} in templates/base.html before </body>. No other files.

Behavior:
- sessionStorage flag ("contest-seen"): set when the overlay is closed or an entry is submitted; if set, never show again this session.
- 1998 banner-ad aesthetics: flashing rainbow gradient background, scrolling marquee strips top and bottom, spinning/pulsing starburst badges, bouncing headline, emoji confetti rain (🐍🎉🏆). CSS animations only, no libraries. Respect prefers-reduced-motion by toning down animations.
- Sounds via Web Audio API only (no audio files): honk/party-horn on button interactions, cheesy fanfare on successful entry. Never attempt autoplay before a user gesture.
- Entry: a drawing canvas (mouse + touch/pointer events) where the user draws a python; "Μαλακία" button clears it. Form with Όνομα and Email inputs, Turnstile widget (sitekey 0x4AAAAAACjhhMHzs4kxktwU, same as present.html), submit button "ΣΥΜΜΕΤΟΧΗ!!!".
- Load https://challenges.cloudflare.com/turnstile/v0/api.js lazily, only when the overlay actually opens (do not add page weight for return visitors).
- Submit: canvas.toBlob PNG posted as multipart/form-data to /api/contest with fields name, email, cf-turnstile-response, drawing. Client-side checks before POST: non-empty canvas (track whether any stroke happened), non-empty name/email.
- Close button: small ×; the first time the pointer hovers it, it jumps to another corner of the overlay; second attempt works and closes.

Exact copy (verbatim, Greek):
- Marquee strips: 🎉 ΜΕΓΑΛΟΣ ΔΙΑΓΩΝΙΣΜΟΣ 🎉 (repeated)
- Headline: ΜΕΓΑΛΟΣ ΔΙΑΓΩΝΙΣΜΟΣ!!!
- Subhead: Κερδίστε ΔΥΟ (2) εισιτήρια για το PyCon 2026!!!
- Starburst badges: ΑΛΗΘΙΝΟ! / 100% ΔΩΡΕΑΝ ΣΥΜΜΕΤΟΧΗ / ΚΕΡΔΙΣΤΕ ΤΩΡΑ!
- Body: Ναι, καλά διαβάσατε, δύο δωρεάν εισιτήρια για το εντελώς πραγματικό συνέδριο PyCon 2026, που σίγουρα θα γίνει.
- Instructions: Για να λάβετε μέρος, ζωγραφίστε έναν πύθωνα. Ναι, τώρα. Ναι, εδώ. Με το ποντίκι. Η καλλιτεχνική επιτροπή περιμένει.
- Labels: Όνομα / Email. Clear button: Μαλακία. Submit: ΣΥΜΜΕΤΟΧΗ!!!
- While submitting: Η επιτροπή κοιτάει το φίδι σας…
- Success: Η συμμετοχή σας καταχωρήθηκε! Ο πύθωνάς σας είναι υπέροχος.** Ο νικητής θα ανακοινωθεί στο Discord. Καλή επιτυχία!
- Empty canvas error: Ο καμβάς είναι άδειος. Η επιτροπή δεν δέχεται αόρατους πύθωνες.
- Missing fields error: Άμα δεν ξέρουμε πού να σας βρούμε θα πάμε εμείς.
- Network/server error: Άμα δε μπορείτε να έχετε ίντερνετ για μισό λεπτό, δε σας αξίζει να πάτε πουθενά.
- Fine print: * Θέλουμε φωτογραφίες και παρουσίαση μετά για αντάλλαγμα ** Πιθανότατα δεν είναι

API contract (already fixed, implemented separately in functions/api/contest.js): POST /api/contest multipart with name, email, cf-turnstile-response, drawing (PNG <= 200KB); 200 {"ok":true} on success, 4xx/5xx {"error":...} otherwise. In local dev (manage.py runserver) the endpoint does not exist; the error path is what you can exercise locally.

Non-goals: no backend changes, no changes to other templates' content, no external JS/CSS libraries, no audio files.

## Acceptance Criteria

Overlay appears once per session on any page, is dismissible, draws on desktop and touch, plays sounds only after user gesture, validates inputs with the exact Greek copy above, and submits multipart form to /api/contest. Overlay markup does not break existing pages (check with Playwright MCP against localhost:8000).


## Notes

**2026-09-04T20:49:58Z**

ready for implementation
