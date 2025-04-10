from datetime import datetime

def log_info(message):
    print(f"[{datetime.now().isoformat()}] {message}")
