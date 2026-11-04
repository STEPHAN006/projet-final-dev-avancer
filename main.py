#!/usr/bin/env python3
"""LifeOS — Personal Operating System
Entry point for launching the application on Linux and Android.
"""

import sys
import argparse
from lifeos.core.database import init_db

def main():
    parser = argparse.ArgumentParser(description="LifeOS — Modern Personal Operating System")
    parser.add_argument("--api-only", action="store_true", help="Run only the FastAPI backend server")
    parser.add_argument("--no-api", action="store_true", help="Run UI without starting background FastAPI server")
    parser.add_argument("--port", type=int, default=8000, help="Port for the FastAPI backend (default 8000)")
    args = parser.parse_args()

    init_db()

    if args.api_only:
        from lifeos.backend.server import run_server
        print(f"🚀 Starting LifeOS FastAPI API on http://127.0.0.1:{args.port} (Docs: http://127.0.0.1:{args.port}/docs)")
        run_server(port=args.port)
        return

    from lifeos.app import LifeOSApp
    app = LifeOSApp(run_api=not args.no_api)
    app.run()

if __name__ == "__main__":
    main()
