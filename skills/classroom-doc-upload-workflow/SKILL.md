---
name: Classroom Doc Upload Workflow
description: First-run login, then rename a file and upload it to Classroom with optional turn-in.
---

# Classroom Doc Upload Workflow

## Trigger

Use this workflow when the user wants first-time Google login, then repeated rename and upload actions to Google Classroom.

## Steps

1. Confirm `web/firebase-config.js` exists, then run `py scripts/launch_login_page.py`.
2. User signs in on login page (Firebase Google sign-in).
3. Confirm `credentials.json` exists for Classroom API OAuth.
4. Run script with `--file`, `--new-name`, `--course-id`, `--coursework-id`.
5. On first API run, complete browser OAuth and persist token for later runs.
6. Rename the file while preserving extension.
7. Upload to Drive, attach to the assignment submission.
8. If requested, pass `--turn-in` to submit.
9. Report final filename, assignment target, and submission state.

## Safety checks

- Do not log secrets, refresh tokens, or credential file contents.
- Request confirmation before overwriting an existing file with the same name.
