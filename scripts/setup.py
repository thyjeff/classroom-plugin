#!/usr/bin/env python3
"""
Google Classroom Uploader - Setup Wizard
First-time setup for Firebase and Google Cloud credentials
"""

import json
import os
import shutil
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

PLUGIN_ROOT = Path(__file__).resolve().parent
WEB_DIR = PLUGIN_ROOT / "web"
CREDENTIALS_FILE = PLUGIN_ROOT / "credentials.json"
FIREBASE_CONFIG = WEB_DIR / "firebase-config.js"


def print_step(num, text):
    print(f"\n{'='*50}")
    print(f"Step {num}: {text}")
    print('='*50)


def check_python_packages():
    print_step(0, "Checking Python packages...")
    required = ["google-auth", "google-auth-oauthlib", "google-api-python-client"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            missing.append(pkg)
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print("Installing...")
        os.system(f'py -m pip install {" ".join(missing)}')
    else:
        print("All packages installed!")


def setup_firebase():
    print_step(1, "Setup Firebase (for login page)")
    print("""
Go to https://console.firebase.google.com/
1. Create a new Firebase project (or use existing)
2. Go to Project Settings → Your apps → Web app
3. Copy the firebaseConfig values
""")
    
    if FIREBASE_CONFIG.exists():
        print(f"Firebase config already exists at: {FIREBASE_CONFIG}")
        cont = input("Overwrite? (y/N): ").strip().lower()
        if cont != 'y':
            return

    print("\nEnter your Firebase config:")
    config = {}
    fields = ["apiKey", "authDomain", "projectId", "storageBucket", "messagingSenderId", "appId"]
    
    for field in fields:
        config[field] = input(f"  {field}: ").strip()
    
    content = f'''export const firebaseConfig = {{
  apiKey: "{config['apiKey']}",
  authDomain: "{config['authDomain']}",
  projectId: "{config['projectId']}",
  storageBucket: "{config['storageBucket']}",
  messagingSenderId: "{config['messagingSenderId']}",
  appId: "{config['appId']}"
}};'''
    
    FIREBASE_CONFIG.write_text(content, encoding="utf-8")
    print(f"✓ Saved to {FIREBASE_CONFIG}")


def setup_google_cloud():
    print_step(2, "Setup Google Cloud OAuth Credentials")
    print("""
1. Go to https://console.cloud.google.com/
2. Select or create a project
3. Enable these APIs:
   - Google Classroom API
   - Google Drive API
4. Go to APIs & Services → Credentials
5. Click 'Create Credentials' → 'OAuth client ID'
6. Application type: Desktop app
7. Download the JSON file
""")
    
    input("Press Enter after creating credentials...")
    
    downloaded = input("Drag & drop the JSON file here (or press Enter to paste content): ").strip()
    
    if os.path.exists(downloaded):
        shutil.copy(downloaded, CREDENTIALS_FILE)
        print(f"✓ Saved to {CREDENTIALS_FILE}")
    elif downloaded:
        try:
            creds = json.loads(downloaded)
            CREDENTIALS_FILE.write_text(json.dumps(creds, indent=2), encoding="utf-8")
            print(f"✓ Saved to {CREDENTIALS_FILE}")
        except json.JSONDecodeError:
            print("Invalid JSON. Please download credentials from Google Cloud Console.")
            return False
    else:
        print("No file provided. Please try again.")
        return False
    
    return True


def setup_oauth_consent():
    print_step(3, "Configure OAuth Consent Screen")
    print("""
In Google Cloud Console (https://console.cloud.google.com/):
1. Go to APIs & Services → OAuth consent screen
2. Choose 'External' (or 'Internal' for GSuite)
3. Fill in required fields:
   - App name: Classroom Uploader
   - User support email: your email
   - Developer email: your email
4. Click 'Add or remove scopes'
5. Add these scopes:
   - .../auth/classroom.courses.readonly
   - .../auth/classroom.coursework.me
   - .../auth/classroom.student-submissions.me.readonly
   - .../auth/drive.file
6. Click 'Save and continue'
7. Add yourself as a test user (if not verified)
""")
    
    input("Press Enter when done...")


def check_api_enabled():
    print_step(4, "Verify APIs are enabled")
    print("""
Make sure these APIs are enabled:
- https://console.developers.google.com/apis/api/classroom.googleapis.com
- https://console.developers.google.com/apis/api/drive.googleapis.com
""")
    input("Press Enter when both APIs are enabled...")


def test_connection():
    print_step(5, "Test Connection")
    print("Running: python scripts/classroom_upload.py --list-courses")
    print("(This will open browser for OAuth authorization)")
    
    os.system(f'py "{PLUGIN_ROOT}/scripts/classroom_upload.py" --list-courses')


def main():
    print("""
╔════════════════════════════════════════════════════╗
║   Google Classroom Uploader - Setup Wizard       ║
║                                                 ║
║   This will guide you through setting up:       ║
║   1. Firebase config (login page)                ║
║   2. Google Cloud OAuth credentials             ║
║   3. OAuth consent screen                       ║
║   4. Enable APIs                                 ║
║   5. Test connection                             ║
╚════════════════════════════════════════════════════╝
    """)
    
    check_python_packages()
    setup_firebase()
    
    if not setup_google_cloud():
        print("\nSetup incomplete. Please run again after getting credentials.")
        return
    
    setup_oauth_consent()
    check_api_enabled()
    test_connection()
    
    print("""
╔════════════════════════════════════════════════════╗
║              Setup Complete!                     ║
║                                                 ║
║   Now you can use:                              ║
║   - classroom-upload                            ║
║   - classroom-drive-only                        ║
║   - classroom-list-courses                     ║
║   - classroom-list-coursework                  ║
║   - classroom-create-assignment                 ║
╚════════════════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
