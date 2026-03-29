import unittest
import threading
import requests
from http.server import HTTPServer
import main

class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(('localhost', 8080), main.MyServer)
        cls.thread = threading.Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    # Test 1
    def test_jwks_returns_200(self):
        response = requests.get("http://localhost:8080/.well-known/jwks.json")
        self.assertEqual(response.status_code, 200)

    def test_jwks_has_keys(self):
        response = requests.get("http://localhost:8080/.well-known/jwks.json")
        data = response.json()
        self.assertIn("keys", data)
        self.assertGreater(len(data["keys"]), 0)

    # Test 2
    def test_auth_returns_jwt(self):
        response = requests.post("http://localhost:8080/auth")
        self.assertEqual(response.status_code, 200)
        token = response.text
        self.assertEqual(len(token.split(".")), 3)

    # Test 3
    def test_auth_expired_returns_jwt(self):
        response = requests.post("http://localhost:8080/auth?expired=true")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.text.split(".")), 3)

    # Test 4
    def test_put_returns_405(self):
        response = requests.put("http://localhost:8080/auth")
        self.assertEqual(response.status_code, 405)

    def test_delete_returns_405(self):
        response = requests.delete("http://localhost:8080/auth")
        self.assertEqual(response.status_code, 405)

    def test_patch_returns_405(self):
        response = requests.patch("http://localhost:8080/auth")
        self.assertEqual(response.status_code, 405)

    # Test 5
    def test_auth_with_basic_auth(self):
        response = requests.post("http://localhost:8080/auth", auth=("userABC", "password123"))
        self.assertEqual(response.status_code, 200)

    def test_auth_with_json_body(self):
        response = requests.post("http://localhost:8080/auth", json={"username": "userABC", "password": "password123"})
        self.assertEqual(response.status_code, 200)
