import json
from urllib.parse import urlsplit

from django.test import TestCase
from django.urls import resolve

from services.common.auth import issue_token
from services.common.contracts import PUBLIC_API_CONTRACTS, route_patterns
from services.user_service.config.urls import urlpatterns
from services.user_service.users.models import User


class UserApiTests(TestCase):
    def post(self, path, payload, token=None):
        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
        return self.client.post(
            path, data=json.dumps(payload), content_type="application/json", **headers
        )

    def patch(self, path, payload, token):
        return self.client.patch(
            path,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

    def test_register_login_and_read_profile(self):
        response = self.post(
            "/register",
            {
                "username": "alice",
                "password": "secret123",
                "phone": "13800138000",
                "usertype": 0,
            },
        )
        self.assertEqual(response.status_code, 201)
        user_id = response.json()["user"]["id"]
        response = self.post("/login", {"username": "alice", "password": "secret123"})
        self.assertEqual(response.status_code, 200)
        token = response.json()["access_token"]
        response = self.client.get(
            f"/users/{user_id}", HTTP_AUTHORIZATION=f"Bearer {token}"
        )
        self.assertEqual(response.json()["user"]["username"], "alice")

    def test_registration_rejects_weak_password(self):
        response = self.post(
            "/register",
            {"username": "alice", "password": "weak", "phone": "13800138000"},
        )
        self.assertEqual(response.status_code, 400)

    def test_duplicate_username_is_rejected(self):
        payload = {
            "username": "alice",
            "password": "secret123",
            "phone": "13800138000",
        }
        self.assertEqual(self.post("/register", payload).status_code, 201)
        self.assertEqual(self.post("/register", payload).status_code, 409)

    def test_user_cannot_read_another_profile(self):
        alice = User.objects.create(
            username="alice", password="unused", phone="13800138000", usertype=0
        )
        bob = User.objects.create(
            username="bob", password="unused", phone="13800138001", usertype=0
        )
        response = self.client.get(
            f"/users/{bob.id}",
            HTTP_AUTHORIZATION=f"Bearer {issue_token(alice.id, 0)}",
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_can_disable_user_and_change_role(self):
        admin = User.objects.create(
            username="admin", password="unused", phone="13800138001", usertype=3
        )
        user = User.objects.create(
            username="bob", password="unused", phone="13800138002", usertype=0
        )
        token = issue_token(admin.id, 3)
        response = self.patch(f"/users/{user.id}/status", {"is_active": False}, token)
        self.assertEqual(response.status_code, 200)
        response = self.patch(f"/users/{user.id}/role", {"usertype": 2}, token)
        self.assertEqual(response.json()["user"]["usertype"], 2)

    def test_internal_batch_lookup(self):
        user = User.objects.create(
            username="bob", password="unused", phone="13800138002", usertype=0
        )
        response = self.client.get(
            f"/internal/users?ids={user.id}", HTTP_X_INTERNAL_TOKEN="dev-internal-token"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["users"][0]["id"], user.id)

    def test_all_exposed_api_methods_match_contract(self):
        contract = set(PUBLIC_API_CONTRACTS["user-service"])
        self.assertEqual(
            route_patterns(urlpatterns), {path for _method, path in contract}
        )
        covered = set()

        def call(method, path, payload=None, token=None, **headers):
            kwargs = dict(headers)
            if token:
                kwargs["HTTP_AUTHORIZATION"] = f"Bearer {token}"
            request = getattr(self.client, method.lower())
            if payload is None:
                response = request(path, **kwargs)
            else:
                response = request(
                    path,
                    data=json.dumps(payload),
                    content_type="application/json",
                    **kwargs,
                )
            route = f"/{resolve(urlsplit(path).path).route}"
            covered.add((method, route))
            self.assertLess(response.status_code, 400, f"{method} {path}")
            return response

        call("GET", "/health/live")
        call("GET", "/health/ready")
        call("GET", "/health/version")
        registered = call(
            "POST",
            "/register",
            {
                "username": "contract-user",
                "password": "secret123",
                "phone": "13800138100",
                "usertype": 0,
            },
        )
        user_id = registered.json()["user"]["id"]
        logged_in = call(
            "POST",
            "/login",
            {"username": "contract-user", "password": "secret123"},
        )
        user_token = logged_in.json()["access_token"]
        admin = User.objects.create(
            username="contract-admin",
            password="unused",
            phone="13800138101",
            usertype=3,
        )
        admin_token = issue_token(admin.id, 3)

        call("POST", "/logout", {}, user_token)
        call("GET", f"/users/{user_id}", token=user_token)
        call(
            "PATCH",
            f"/users/{user_id}/profile",
            {"phone": "13800138102", "word": "updated"},
            user_token,
        )
        call(
            "PATCH",
            f"/users/{user_id}/status",
            {"is_active": False},
            admin_token,
        )
        call(
            "PATCH",
            f"/users/{user_id}/role",
            {"usertype": 1},
            admin_token,
        )
        call(
            "GET",
            f"/internal/users?ids={admin.id}",
            HTTP_X_INTERNAL_TOKEN="dev-internal-token",
        )
        self.assertEqual(covered, contract)
