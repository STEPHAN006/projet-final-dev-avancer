"""Background runner for FastAPI in LifeOS."""

import threading
import uvicorn
from lifeos.backend.app import app

_server_thread = None

def run_server(host: str = "127.0.0.1", port: int = 8000):
    config = uvicorn.Config(app=app, host=host, port=port, log_level="warning")
    server = uvicorn.Server(config)
    server.run()

def start_background_server(host: str = "127.0.0.1", port: int = 8000) -> threading.Thread:
    global _server_thread
    if _server_thread is not None and _server_thread.is_alive():
        return _server_thread
    _server_thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    _server_thread.start()
    return _server_thread

if __name__ == "__main__":
    print("Starting LifeOS FastAPI on http://127.0.0.1:8000 (Docs: http://127.0.0.1:8000/docs)")
    run_server()
