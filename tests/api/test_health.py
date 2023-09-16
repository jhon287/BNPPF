from unittest import TestCase
from fastapi.testclient import TestClient
from httpx import Response, codes
from main import api


class HealthTests(TestCase):
    client: TestClient = TestClient(app=api)

    def test_get_health(self):
        response: Response = self.client.get("/health")
        self.assertEqual(first=response.status_code, second=codes.OK)
        self.assertEqual(first=response.json(), second={"status": "OK"})

    def test_get_health_service(self):
        # 200 OK - status OK
        response: Response = self.client.get("/health/database")
        self.assertEqual(first=response.status_code, second=codes.OK)
        self.assertEqual(
            first=response.json(), second={"service": "database", "status": "OK"}
        )
        # 404 Not Found - No such service!
        self.assertEqual(
            first=self.client.get("/health/pouet").status_code, second=codes.NOT_FOUND
        )
