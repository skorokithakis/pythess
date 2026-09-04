---
id: rep-kwtyc
status: closed
deps: []
links: []
created: 2026-09-04T20:44:36Z
type: task
priority: 2
assignee: Stavros Korokithakis
---
# Contest entry API: functions/api/contest.js

Objective: Cloudflare Pages Function that receives contest entries and posts them to Discord.

Follow the existing pattern in functions/api/present.js (Turnstile verification first, then field validation, then Discord webhook).

Endpoint contract (fixed, the overlay frontend is built against it):
- POST /api/contest, multipart/form-data with fields: name, email, cf-turnstile-response, drawing (a PNG file blob of the entrant's snake drawing).
- Validate: Turnstile token via TURNSTILE_SECRET_KEY (403 on failure), name and email non-empty, email contains "@", drawing present, is image/png, and <= 200KB (400 with {"error": ...} otherwise).
- Post to env.DISCORD_WEBHOOK_URL (same webhook as presentation proposals, per owner decision) as multipart: an embed titled "Νέα συμμετοχή στον ΜΕΓΑΛΟ ΔΙΑΓΩΝΙΣΜΟ" with Name/Email fields and timestamp, plus the drawing attached as an image file and referenced in the embed via attachment:// so it renders inline.
- 502 {"error": "Failed to send notification"} if Discord rejects; 200 {"ok": true} on success.

Non-goals: no Django views, no models, no migrations, no storage besides Discord. Do not modify present.js.

Caveat: Discord webhook file upload requires multipart/form-data with a payload_json part for the embed JSON; do not send Content-Type application/json.

## Acceptance Criteria

POST with valid Turnstile token, name, email, and small PNG returns 200 and would post embed+attachment to the webhook; missing/oversized/non-PNG drawing, missing fields, or bad token return the specified error statuses.


## Notes

**2026-09-04T20:49:58Z**

ready for implementation
