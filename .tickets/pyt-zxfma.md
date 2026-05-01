---
id: pyt-zxfma
status: closed
deps: [pyt-lsilx]
links: []
created: 2026-05-01T23:34:31Z
type: task
priority: 2
assignee: Stavros Korokithakis
---
# Inline markdown preview for create-meetup description

Below the description textarea on /create-meetup/, show a live-rendered markdown preview that updates as the user types.

- Use the 'marked' library from a CDN (jsdelivr or unpkg). Pin a specific version.
- Render the preview into a styled container below the textarea (e.g. a div with a subtle border / background so it's visually distinct from the input).
- Update on 'input' events on the textarea.
- Initialize on page load with whatever value is currently in the textarea (so it works after autosave restores a draft).
- Server-side: nothing changes.
- Sanitization: the preview is only ever shown to staff users on their own input, so sanitization is not required. Do not add DOMPurify or similar.

Non-goals:
- No syntax highlighting for code blocks.
- No toggle to hide the preview.
- No matching the exact markdownify rendering — close enough is fine; this is a preview, not a final render.

## Acceptance Criteria

Typing markdown in the description field on /create-meetup/ produces a live HTML preview below the textarea. After a localStorage draft restore, the preview reflects the restored content.

