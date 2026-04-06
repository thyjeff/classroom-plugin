# classroom-plugin

A CLI plugin for uploading documents to Google Classroom — with automatic fallback to Drive links when Classroom API restrictions apply. Works with Cursor, Claude, and any AI agent, or standalone from the terminal.

---

## Features

- Upload files to Google Classroom assignments
- Auto-fallback to Google Drive link on API permission errors
- List courses and assignments
- Create new assignments via CLI
- OAuth 2.0 authentication (token persisted locally)
- Dry-run mode for safe validation before upload
- Works with Cursor, Claude Code, GitHub Copilot, or standalone CLI

---

## Prerequisites

- Python 3.10+
- A Google Cloud project with **Classroom API** and **Drive API** enabled
- A Firebase project (for the local login page)

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Setup (First Time)

Run the interactive setup wizard:

```bash
python scripts/setup.py
```

This guides you through:
1. Firebase config (for the local login page)
2. Google Cloud OAuth credentials
3. OAuth consent screen configuration
4. API enablement check
5. Connection test

---

## Usage

### List courses
```bash
python scripts/classroom_upload.py --list-courses
```

### List assignments for a course
```bash
python scripts/classroom_upload.py --list-coursework --course-id "COURSE_ID"
```

### Upload and turn in
```bash
python scripts/classroom_upload.py \
  --file "homework.docx" \
  --new-name "Homework-1.docx" \
  --course-id "123456" \
  --coursework-id "789012" \
  --turn-in
```

### Upload to Drive only (skip Classroom)
```bash
python scripts/classroom_upload.py \
  --file "doc.docx" \
  --new-name "doc-renamed.docx" \
  --drive-only
```

### Dry run (validate without uploading)
```bash
python scripts/classroom_upload.py \
  --file "doc.docx" \
  --new-name "doc-renamed.docx" \
  --course-id "123456" \
  --coursework-id "789012" \
  --dry-run
```

---

## CLI Reference

| Flag | Description |
|---|---|
| `--file PATH` | Path to the local file |
| `--new-name NAME` | New filename (extension must match unless `--allow-extension-change`) |
| `--course-id ID` | Google Classroom course ID |
| `--coursework-id ID` | Google Classroom coursework ID |
| `--turn-in` | Submit the assignment after attaching |
| `--drive-only` | Upload to Drive only, skip Classroom |
| `--dry-run` | Validate auth and rename without modifying files |
| `--allow-extension-change` | Allow renaming to a different extension |
| `--list-courses` | List all enrolled courses |
| `--list-coursework` | List assignments for a course (requires `--course-id`) |
| `--create-assignment` | Create a new assignment (requires `--course-id` and `--assignment-title`) |

---

## AI Agent Integration

### Cursor
Plugin files are in `.cursor-plugin/`. Cursor picks them up automatically from the project root.

### Claude / Claude Code
Drop the `agents/`, `commands/`, and `skills/` folders into your Claude project config.

### Other agents
Use the `commands/` markdown files as prompts or tool definitions.

---

## Troubleshooting

### `@ProjectPermissionDenied` error
This occurs when the assignment was created manually in Classroom rather than via API.

**Solutions:**
- Create the assignment via API: `--create-assignment`
- Use `--drive-only` and paste the Drive link manually into Classroom
- Run the upload within 24 hours of creating the assignment in Classroom

### Missing APIs
Enable these in [Google Cloud Console](https://console.cloud.google.com/):
- Google Classroom API
- Google Drive API

### Token expired
Delete `token.json` and re-authenticate:
```bash
rm token.json
```

---

## Security

- `credentials.json` and `token.json` are excluded from version control via `.gitignore`
- Never commit OAuth credentials or tokens
- The Firebase config in `web/firebase-config.js` is also gitignored — only the example file is tracked

---

## License

MIT
