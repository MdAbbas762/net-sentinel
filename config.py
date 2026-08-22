from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_FILE = DATA_DIR / "firewall_logs.txt"

RATE_LIMIT = 5
TRUSTED_IPS = {"127.0.0.1"}
SECURITY_LEVELS = {"low": 1, "medium": 2, "high": 3}

BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 8080
FIREWALL_HOST = "0.0.0.0"
FIREWALL_PORT = 9090
ADMIN_HOST = "127.0.0.1"
ADMIN_PORT = 9999

ADMIN_CREDENTIALS = {"admin": "123"}
