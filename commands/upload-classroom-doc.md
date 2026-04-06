---
name: Upload Classroom Document
description: First-time login, then rename and upload a document to Classroom with optional turn-in.
---

Execute this workflow:

1. Ask for:
   - file location
   - new filename
   - Classroom `course-id`
   - Classroom `coursework-id`
   - whether to `turn in` now
2. Ensure `web/firebase-config.js` is present, then run:
   - `py scripts/launch_login_page.py`
3. User completes login on page.
4. Ensure `credentials.json` is present in plugin root.
5. Run:
   - `py scripts/classroom_upload.py --file "<path>" --new-name "<name.ext>" --course-id "<id>" --coursework-id "<id>" [--turn-in]`
6. If first API run, user completes Google login in browser.
7. Confirm result and return:
   - old filename
   - new filename
   - destination course/assignment
   - upload confirmation status
   - turn-in status
