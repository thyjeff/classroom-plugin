import argparse
import json
import mimetypes
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.coursework.me",
    "https://www.googleapis.com/auth/classroom.student-submissions.me.readonly",
    "https://www.googleapis.com/auth/drive.file",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rename a local file, upload to Google Classroom assignment, and optionally turn in."
    )
    parser.add_argument("--list-courses", action="store_true", help="List all courses")
    parser.add_argument("--list-coursework", action="store_true", help="List all coursework for a course")
    parser.add_argument("--create-assignment", action="store_true", help="Create a new assignment")
    parser.add_argument("--drive-only", action="store_true", help="Upload to Drive only (skip Classroom)")
    parser.add_argument("--file", type=str, help="Path to local file")
    parser.add_argument("--new-name", type=str, help="New filename including extension")
    parser.add_argument("--course-id", type=str, help="Classroom course ID")
    parser.add_argument("--coursework-id", type=str, help="Classroom coursework ID")
    parser.add_argument("--assignment-title", type=str, help="Title for new assignment")
    parser.add_argument(
        "--turn-in",
        action="store_true",
        help="Turn in submission after attaching uploaded file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate auth and rename rules without modifying files or uploading",
    )
    parser.add_argument(
        "--allow-extension-change",
        action="store_true",
        help="Allow changing the file extension during rename",
    )
    return parser.parse_args()


def plugin_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_credentials(root: Path) -> Credentials:
    token_path = root / "token.json"
    creds_path = root / "credentials.json"
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError(
                    "Missing credentials.json in plugin root. "
                    "Create OAuth desktop credentials and save as credentials.json."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        token_path.write_text(creds.to_json(), encoding="utf-8")

    return creds


def rename_file(source_file: Path, new_name: str) -> Path:
    if not source_file.exists():
        raise FileNotFoundError(f"File not found: {source_file}")

    if not source_file.is_file():
        raise ValueError(f"Path is not a file: {source_file}")

    target_file = source_file.with_name(new_name)
    if target_file.exists():
        raise FileExistsError(
            f"Target filename already exists: {target_file}. "
            "Pick a different --new-name."
        )

    source_file.rename(target_file)
    return target_file


def validate_rename(source: Path, new_name: str, allow_extension_change: bool) -> None:
    if Path(new_name).name != new_name:
        raise ValueError("--new-name must be a filename only, not a path.")

    if not allow_extension_change and source.suffix.lower() != Path(new_name).suffix.lower():
        raise ValueError(
            "File extension must stay the same. "
            "Use --allow-extension-change to override."
        )


def upload_to_drive(file_path: Path, drive_service) -> str:
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    metadata = {"name": file_path.name}
    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)
    created = (
        drive_service.files()
        .create(body=metadata, media_body=media, fields="id,name")
        .execute()
    )
    return created["id"]


def get_submission(classroom_service, course_id: str, coursework_id: str) -> str:
    result = (
        classroom_service.courses()
        .courseWork()
        .studentSubmissions()
        .list(
            courseId=course_id,
            courseWorkId=coursework_id,
            userId="me",
            pageSize=1,
        )
        .execute()
    )
    submissions = result.get("studentSubmissions", [])
    if not submissions:
        raise RuntimeError(
            "No student submission found. Confirm course/work IDs and account access."
        )
    return submissions[0]["id"]


def attach_drive_file(
    classroom_service,
    course_id: str,
    coursework_id: str,
    submission_id: str,
    drive_file_id: str,
) -> dict:
    body = {"addAttachments": [{"driveFile": {"id": drive_file_id}}]}
    return (
        classroom_service.courses()
        .courseWork()
        .studentSubmissions()
        .modifyAttachments(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            body=body,
        )
        .execute()
    )


def turn_in_submission(
    classroom_service, course_id: str, coursework_id: str, submission_id: str
) -> dict:
    return (
        classroom_service.courses()
        .courseWork()
        .studentSubmissions()
        .turnIn(
            courseId=course_id,
            courseWorkId=coursework_id,
            id=submission_id,
            body={},
        )
        .execute()
    )


def fail(message: str, details: str | None = None) -> None:
    payload: dict[str, Any] = {"status": "error", "message": message}
    if details:
        payload["details"] = details
    print(json.dumps(payload, indent=2))
    raise SystemExit(1)


def list_courses(classroom_service) -> list[dict]:
    result = classroom_service.courses().list(pageSize=100).execute()
    courses = result.get("courses", [])
    return [
        {
            "id": c.get("id"),
            "name": c.get("name"),
            "section": c.get("section", ""),
            "state": c.get("courseState", ""),
        }
        for c in courses
    ]


def list_coursework(classroom_service, course_id: str) -> list[dict]:
    result = (
        classroom_service.courses()
        .courseWork()
        .list(courseId=course_id, pageSize=100)
        .execute()
    )
    coursework = result.get("courseWork", [])
    return [
        {
            "id": cw.get("id"),
            "title": cw.get("title"),
            "dueDate": cw.get("dueDate", {}),
            "state": cw.get("state", ""),
            "description": cw.get("description", ""),
        }
        for cw in coursework
    ]


def create_assignment(classroom_service, course_id: str, title: str) -> dict:
    body = {
        "title": title,
        "state": "PUBLISHED",
    }
    result = (
        classroom_service.courses()
        .courseWork()
        .create(courseId=course_id, body=body)
        .execute()
    )
    return {
        "id": result.get("id"),
        "title": result.get("title"),
        "state": result.get("state"),
    }


def upload_to_drive_and_get_link(drive_service, file_path: Path) -> tuple[str, str]:
    mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    metadata = {"name": file_path.name}
    media = MediaFileUpload(str(file_path), mimetype=mime_type, resumable=True)
    created = (
        drive_service.files()
        .create(body=metadata, media_body=media, fields="id,name,webViewLink")
        .execute()
    )
    link = created.get("webViewLink", f"https://drive.google.com/file/d/{created.get('id')}/view")
    return created["id"], link


def main() -> None:
    args = parse_args()
    root = plugin_root()
    renamed: Path | None = None

    try:
        creds = get_credentials(root)
        classroom = build("classroom", "v1", credentials=creds)

        if args.list_courses:
            courses = list_courses(classroom)
            print(json.dumps({"status": "ok", "courses": courses}, indent=2))
            return

        if args.list_coursework:
            if not args.course_id:
                fail("--course-id is required with --list-coursework")
            coursework = list_coursework(classroom, args.course_id)
            print(json.dumps({"status": "ok", "coursework": coursework}, indent=2))
            return

        if args.create_assignment:
            if not args.course_id or not args.assignment_title:
                fail("--course-id and --assignment-title are required for creating assignment")
            assignment = create_assignment(classroom, args.course_id, args.assignment_title)
            print(json.dumps({"status": "ok", "assignment": assignment}, indent=2))
            return

        source = Path(args.file).expanduser().resolve()
        validate_rename(source, args.new_name, args.allow_extension_change)
        
        drive = build("drive", "v3", credentials=creds)
        
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "status": "ok",
                        "dry_run": True,
                        "old_filename": source.name,
                        "new_filename": args.new_name,
                        "course_id": args.course_id,
                        "coursework_id": args.coursework_id,
                    },
                    indent=2,
                )
            )
            return

        renamed = rename_file(source, args.new_name)
        drive_file_id, drive_link = upload_to_drive_and_get_link(drive, renamed)
        
        if args.drive_only:
            print(json.dumps({
                "status": "ok",
                "message": "File uploaded to Drive only",
                "drive_link": drive_link,
                "filename": renamed.name,
            }, indent=2))
            return

        try:
            submission_id = get_submission(classroom, args.course_id, args.coursework_id)
            attach_drive_file(
                classroom, args.course_id, args.coursework_id, submission_id, drive_file_id
            )

            turned_in = False
            if args.turn_in:
                turn_in_submission(classroom, args.course_id, args.coursework_id, submission_id)
                turned_in = True

            result = {
                "old_filename": source.name,
                "new_filename": renamed.name,
                "course_id": args.course_id,
                "coursework_id": args.coursework_id,
                "submission_id": submission_id,
                "drive_link": drive_link,
                "turned_in": turned_in,
                "status": "ok",
            }
            print(json.dumps(result, indent=2))
        except HttpError as exc:
            print(json.dumps({
                "status": "partial",
                "message": "Uploaded to Drive but Classroom attachment failed",
                "drive_link": drive_link,
                "error": str(exc),
                "instruction": "Manually add the Drive link to your submission in Classroom",
            }, indent=2))
            
    except HttpError as exc:
        if renamed and renamed.exists() and not source.exists():
            renamed.rename(source)
        fail("Google API request failed.", str(exc))
    except (OSError, ValueError, RuntimeError) as exc:
        if renamed and renamed.exists() and not source.exists():
            renamed.rename(source)
        fail(str(exc))


if __name__ == "__main__":
    main()
