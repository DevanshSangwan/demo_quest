import json
import os
from typing import Optional

import firebase_admin
from firebase_admin import auth, credentials, firestore


def _resolve_service_account_path() -> Optional[str]:
    """
    Resolve a usable path to a Firebase service account key JSON.
    Priority:
    1) GOOGLE_APPLICATION_CREDENTIALS env var
    2) ServiceAccountKey.json in current working directory
    3) ServiceAccountKey.json at project root (two directories up)
    """
    env_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if env_path and os.path.isfile(env_path):
        return env_path

    module_dir = os.path.dirname(__file__)
    local_path_module = os.path.join(module_dir, "ServiceAccountKey.json")
    if os.path.isfile(local_path_module):
        return local_path_module
    # No further fallbacks to avoid ambiguity

    return None


def _init_firebase_app() -> None:
    if firebase_admin._apps:
        return

    sa_path = _resolve_service_account_path()
    if sa_path:
        cred = credentials.Certificate(sa_path)
        firebase_admin.initialize_app(cred)
        return

    try:
        firebase_admin.initialize_app()
    except Exception as exc:
        raise RuntimeError(
            "Failed to initialize Firebase Admin SDK. Provide a valid service "
            "account JSON (e.g., place ServiceAccountKey.json alongside "
            "app/firebase_config.py or set GOOGLE_APPLICATION_CREDENTIALS)."
        ) from exc


_init_firebase_app()

# Expose Firestore client and auth for the rest of the app
_database_id = os.getenv("FIRESTORE_DATABASE_ID")
if _database_id:
    db = firestore.client(database=_database_id)
else:
    db = firestore.client()
firebase_auth = auth


def get_firebase_web_config():
    """
    Compatibility helper mirroring the root-level helper if needed elsewhere.
    Prefers firebase_web_config.json; otherwise constructs partial config.
    """
    config_file = os.path.join(os.path.dirname(__file__), "firebase_web_config.json")
    if os.path.exists(config_file):
        try:
            with open(config_file, "r") as f:
                config = json.load(f)
            return {k: v for k, v in config.items() if not k.startswith("_")}
        except Exception:
            pass

    # Attempt to infer projectId from service account
    sa_path = _resolve_service_account_path()
    if sa_path:
        try:
            with open(sa_path, "r") as f:
                service_account = json.load(f)
            project_id = service_account.get("project_id", "")
            if project_id:
                return {
                    "apiKey": "",
                    "authDomain": f"{project_id}.firebaseapp.com",
                    "projectId": project_id,
                }
        except Exception:
            pass

    return {"apiKey": "", "authDomain": "", "projectId": ""}