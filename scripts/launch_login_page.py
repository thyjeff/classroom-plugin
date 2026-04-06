import argparse
import http.server
import os
import socketserver
import threading
import webbrowser
from pathlib import Path


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Launch local Firebase login page.")
    parser.add_argument("--port", type=int, default=8787, help="Port for local web server")
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start server without auto-opening browser",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    web_dir = root / "web"
    cfg = web_dir / "firebase-config.js"

    if not cfg.exists():
        raise FileNotFoundError(
            "Missing web/firebase-config.js. Copy web/firebase-config.example.js to "
            "web/firebase-config.js and fill your Firebase project values."
        )

    os.chdir(web_dir)
    handler = http.server.SimpleHTTPRequestHandler
    with ReusableTCPServer(("", args.port), handler) as httpd:
        url = f"http://localhost:{args.port}/login.html"
        print(f"Login page: {url}")
        if not args.no_browser:
            thread = threading.Thread(target=webbrowser.open, args=(url,), daemon=True)
            thread.start()
        print("Press Ctrl+C to stop server after login.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
