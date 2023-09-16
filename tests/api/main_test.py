from unittest import TestCase
from fastapi.testclient import TestClient
from main import api

class MainTests(TestCase):
    client: TestClient = TestClient(app=api)



    # def test_get_root(self):
    #     response: Response = self.client.get("/")
    #     assert response.status_code == codes.FORBIDDEN
    #     assert response.text == "Access Denied !"

    # def test_head_root(self):
    #     assert 403 == self.client.head("/").status_code

    # def test_get_years(self):
    #     response: Response = self.client.get(url="/years")
    #     assert response.status_code == codes.OK
    #     assert response.text == '[]'
