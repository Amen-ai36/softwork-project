import json

from django.test import TestCase

from services.common.auth import issue_token
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
