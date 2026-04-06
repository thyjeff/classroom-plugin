# Google Classroom Uploader

Upload documents to Google Classroom from CLI, with fallback to Drive links for assignments not created via API.

![PyPI Version](https://img.shields.io/pypi/v/classroom-uploader)
![Python](https://img.shields.io/pypi/pyversions/classroom-uploader)

## Features

- 📤 Upload files to Google Classroom assignments
- 🔄 Auto-fallback to Google Drive link if Classroom API fails
- 📋 List courses and assignments
- ➕ Create new assignments via CLI
- 🔐 OAuth 2.0 authentication
- 🤖 Works with **any AI agent** - OpenCode, Cursor, Claude, GitHub Copilot, or standalone CLI

## Installation

### Prerequisites

```bash
# Install Python dependencies
py -m pip install -r requirements.txt
```

### Setup (First Time)

Run the interactive setup wizard:

```bash
py scripts/setup.py
```

This will guide you through:
1. Firebase config (for login page)
2. Google Cloud OAuth credentials
3. Enable required APIs
4. Test connection

## Quick Usage

```bash
# List your courses
py scripts/classroom_upload.py --list-courses

# List assignments for a course
py scripts/classroom_upload.py --list-coursework --course-id "COURSE_ID"

# Upload file to assignment
py scripts/classroom_upload.py \
  --file "homework.docx" \
  --new-name "John-Homework.docx" \
  --course-id "123456" \
  --coursework-id "789012" \
  --turn-in
```

## Commands

| Command | Description |
|---------|-------------|
| `--list-courses` | List all your Google Classroom courses |
| `--list-coursework --course-id ID` | List assignments in a course |
| `--create-assignment --course-id ID --title "Name"` | Create new assignment |
| `--drive-only` | Upload to Drive only (no Classroom) |

## AI Agent Plugin

Copy the plugin to your agent's plugins directory:

### OpenCode (Global)
```bash
copy plugins\classroom-upload.ts %APPDATA%\opencode\plugins\
```

### OpenCode (Project)
```bash
copy .opencode\plugins\ classroom-uploader.ts
```

### Cursor
The plugin files are already in `.cursor-plugin/` directory.

### Note on OpenCode/Cursor Global Plugins

The OpenCode plugin is stored in your global config:
- **Windows**: `%APPDATA%\OpenCode\plugins\classroom-upload.ts`

For others to use, they need to copy the plugin to their own setup or create their own in their global config directory.

### Available Tools

```python
# Upload to Classroom (auto-fallback to Drive)
classroom-upload --file "doc.docx" --new-name "name.docx" --course-id "123" --coursework-id "456"

# Upload to Drive only
classroom-drive-only --file "doc.docx" --new-name "name.docx"

# List courses
classroom-list-courses

# List coursework
classroom-list-coursework --course-id "123"

# Create assignment
classroom-create-assignment --course-id "123" --title "Homework 1"
```

## Troubleshooting

### "@ProjectPermissionDenied" Error

This happens because the assignment was created manually in Google Classroom, not via API. 

**Solutions:**
1. Create assignments via API: `classroom-create-assignment`
2. Use `--drive-only` and manually paste the Drive link in Classroom
3. Create assignment in Classroom first, then run upload within 24 hours

### Missing APIs

Make sure these APIs are enabled in Google Cloud Console:
- Google Classroom API
- Google Drive API

### Token Expiry

Delete `token.json` to re-authenticate:
```bash
del token.json
```

## Security

- Never commit `credentials.json` or `token.json` to version control
- Add to `.gitignore`:
  ```
  credentials.json
  token.json
  ```

## License

MIT
