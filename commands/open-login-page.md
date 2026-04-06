---
name: Open Classroom Login Page
description: Launch the local Firebase Google login page for first-time sign-in.
---

Run:

- `py scripts/launch_login_page.py`

If browser does not auto-open:

- `py scripts/launch_login_page.py --no-browser`
- Open `http://localhost:8787/login.html` manually.

After sign-in succeeds, continue with:

- `py scripts/classroom_upload.py --file "<path>" --new-name "<name.ext>" --course-id "<id>" --coursework-id "<id>" [--turn-in]`
