from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass
from typing import Any, Dict, Tuple

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.dependencies import get_db  # noqa: E402  (import after sys.path tweak)
from app.main import app  # noqa: E402
import app.routers.auth as auth_router  # noqa: E402


@dataclass
class FakeUser:
    uid: str
    email: str
    password: str
    display_name: str


class FakeDocSnapshot:
    def __init__(self, data: Dict[str, Any] | None) -> None:
        self._data = data

    @property
    def exists(self) -> bool:
        return self._data is not None

    def to_dict(self) -> Dict[str, Any]:
        if self._data is None:
            raise ValueError("No data stored in fake snapshot.")
        return self._data


class FakeDocRef:
    def __init__(self, store: Dict[str, Dict[str, Any]], uid: str) -> None:
        self._store = store
        self._uid = uid

    def set(self, data: Dict[str, Any]) -> None:
        self._store[self._uid] = data

    def get(self) -> FakeDocSnapshot:
        return FakeDocSnapshot(self._store.get(self._uid))


class FakeCollection:
    def __init__(self, store: Dict[str, Dict[str, Any]]) -> None:
        self._store = store

    def document(self, uid: str) -> FakeDocRef:
        return FakeDocRef(self._store, uid)


class FakeFirestoreClient:
    def __init__(self) -> None:
        self._collections: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def collection(self, name: str) -> FakeCollection:
        if name not in self._collections:
            self._collections[name] = {}
        return FakeCollection(self._collections[name])


class FakeFirebaseAuth:
    EmailAlreadyExistsError = ValueError

    def __init__(self) -> None:
        self._users_by_email: Dict[str, FakeUser] = {}

    def create_user(self, *, email: str, password: str, display_name: str) -> FakeUser:
        if email in self._users_by_email:
            raise self.EmailAlreadyExistsError("Email already registered.")

        uid = f"user-{len(self._users_by_email) + 1}"
        user = FakeUser(uid=uid, email=email, password=password, display_name=display_name)
        self._users_by_email[email] = user
        return user

    def create_custom_token(self, uid: str) -> bytes:
        return f"custom-token-{uid}".encode("utf-8")

    def verify_id_token(self, token: str) -> Dict[str, Any]:
        # In tests we allow the token itself to represent the UID.
        return {"uid": token}

    def add_user(
        self,
        *,
        uid: str,
        email: str,
        password: str,
        display_name: str,
    ) -> FakeUser:
        user = FakeUser(uid=uid, email=email, password=password, display_name=display_name)
        self._users_by_email[email] = user
        return user

    def get_user_by_email(self, email: str) -> FakeUser | None:
        return self._users_by_email.get(email)


class FakeResponse:
    def __init__(self, status_code: int, payload: Dict[str, Any]) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> Dict[str, Any]:
        return self._payload


class FakeRequestsModule:
    def __init__(self, firebase_auth: FakeFirebaseAuth) -> None:
        self._auth = firebase_auth
        self.last_signup_token: str | None = None
        self.last_login_token: str | None = None

    def post(self, url: str, json: Dict[str, Any] | None = None, **_: Any) -> FakeResponse:
        if json is None:
            json = {}

        if "signInWithCustomToken" in url:
            custom_token = json.get("token", "")
            token = f"id-token-for-{custom_token}"
            self.last_signup_token = token
            return FakeResponse(200, {"idToken": token})

        if "signInWithPassword" in url:
            email = json.get("email")
            password = json.get("password")
            user = self._auth.get_user_by_email(email) if email else None
            if not user or user.password != password:
                return FakeResponse(400, {"error": {"message": "INVALID_CREDENTIALS"}})

            token = f"id-token-for-{user.uid}"
            self.last_login_token = token
            return FakeResponse(200, {"localId": user.uid, "idToken": token})

        raise AssertionError(f"Unexpected URL received in fake requests module: {url}")


@pytest.fixture()
def test_context(monkeypatch: pytest.MonkeyPatch) -> Tuple[TestClient, FakeFirestoreClient, FakeFirebaseAuth, FakeRequestsModule]:
    fake_db = FakeFirestoreClient()
    fake_auth = FakeFirebaseAuth()
    fake_requests = FakeRequestsModule(fake_auth)

    def _get_db_override() -> FakeFirestoreClient:
        return fake_db

    app.dependency_overrides[get_db] = _get_db_override
    monkeypatch.setattr(auth_router, "firebase_auth", fake_auth)
    monkeypatch.setattr(auth_router, "get_firebase_web_config", lambda: {"apiKey": "fake-api-key"})
    monkeypatch.setattr(auth_router, "requests", fake_requests)

    client = TestClient(app)

    yield client, fake_db, fake_auth, fake_requests

    app.dependency_overrides.pop(get_db, None)


def test_signup_creates_user_and_returns_token(test_context: Tuple[TestClient, FakeFirestoreClient, FakeFirebaseAuth, FakeRequestsModule]) -> None:
    client, fake_db, fake_auth, fake_requests = test_context

    payload = {
        "email": "signup@example.com",
        "password": "supersecret",
        "displayName": "Sign Up User",
    }

    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["user"]["email"] == payload["email"]
    assert body["user"]["displayName"] == payload["displayName"]
    assert body["user"]["totalSubmissions"] == 0
    assert body["token"] == fake_requests.last_signup_token == f"id-token-for-custom-token-{fake_auth.get_user_by_email(payload['email']).uid}"

    stored_user = fake_db.collection("users").document(fake_auth.get_user_by_email(payload["email"]).uid).get().to_dict()
    assert stored_user["email"] == payload["email"]


def test_login_returns_existing_user_profile(test_context: Tuple[TestClient, FakeFirestoreClient, FakeFirebaseAuth, FakeRequestsModule]) -> None:
    client, fake_db, fake_auth, fake_requests = test_context

    existing_user = fake_auth.add_user(
        uid="user-42",
        email="login@example.com",
        password="supersecret",
        display_name="Login User",
    )

    fake_db.collection("users").document(existing_user.uid).set(
        {
            "uid": existing_user.uid,
            "email": existing_user.email,
            "displayName": existing_user.display_name,
            "totalSubmissions": 3,
        }
    )

    payload = {"email": existing_user.email, "password": existing_user.password}

    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["user"]["uid"] == existing_user.uid
    assert body["user"]["totalSubmissions"] == 3
    assert body["token"] == fake_requests.last_login_token == f"id-token-for-{existing_user.uid}"


def test_get_current_user_profile_returns_user_document(test_context: Tuple[TestClient, FakeFirestoreClient, FakeFirebaseAuth, FakeRequestsModule]) -> None:
    client, fake_db, fake_auth, _ = test_context

    uid = "user-me"
    fake_db.collection("users").document(uid).set(
        {
            "uid": uid,
            "email": "me@example.com",
            "displayName": "Me Myself",
            "totalSubmissions": 5,
        }
    )

    auth_router.firebase_auth = fake_auth  # ensure latest reference

    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {uid}"})
    assert response.status_code == 200, response.text

    body = response.json()
    assert body["uid"] == uid
    assert body["displayName"] == "Me Myself"
