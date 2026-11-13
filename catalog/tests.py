from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class CatalogTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        get_user_model().objects.create_user(username="student", password="Demo-Test-Pass123")

    def log_in(self):
        response = self.client.post("/api/token/", {
            "username": "student",
            "password": "Demo-Test-Pass123",
        })
        self.assertEqual(response.status_code, 200)
        tokens = response.json()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        return tokens

    def create(self, section, data):
        response = self.client.post(f"/api/{section}/", data, format="json")
        self.assertEqual(response.status_code, 201, response.content)
        return response.json()["id"]

    def test_catalog_requires_jwt(self):
        for section in ("species", "breeds", "pets"):
            self.assertEqual(self.client.get(f"/api/{section}/").status_code, 401)
            self.assertEqual(self.client.post(f"/api/{section}/", {}).status_code, 401)

    def test_login_and_refresh(self):
        response = self.client.post("/api/token/", {"username": "student", "password": "wrong"})
        self.assertEqual(response.status_code, 401)
        tokens = self.log_in()
        response = self.client.post("/api/token/refresh/", {"refresh": tokens["refresh"]})
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())

    def test_crud_and_pagination(self):
        self.log_in()
        species = self.create("species", {"name": "Кошка"})
        breed = self.create("breeds", {"name": "Сибирская", "species": species})
        pet_data = {"name": "Рыжик", "breed": breed, "age_months": 3, "price": "4500.00"}
        pets = [
            self.create("pets", {**pet_data, "name": f"Рыжик {i}"})
            for i in range(6)
        ]
        for section, object_id, name in (
            ("species", species, "Кошки"),
            ("breeds", breed, "Сибирская кошка"),
            ("pets", pets[0], "Персик"),
        ):
            with self.subTest(section=section):
                listing = self.client.get(f"/api/{section}/").json()
                self.assertIn("results", listing)
                url = f"/api/{section}/{object_id}/"
                self.assertEqual(self.client.get(url).status_code, 200)
                updated = self.client.patch(url, {"name": name})
                self.assertEqual(updated.status_code, 200)
                self.assertEqual(self.client.get(url).json()["name"], name)
        self.assertEqual(len(self.client.get("/api/pets/").json()["results"]), 5)
        self.assertEqual(len(self.client.get("/api/pets/?page=2").json()["results"]), 1)
        for section, ids in (("pets", pets), ("breeds", [breed]), ("species", [species])):
            for object_id in ids:
                url = f"/api/{section}/{object_id}/"
                self.assertEqual(self.client.delete(url).status_code, 204)
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_invalid_values_and_protected_relations(self):
        self.log_in()
        species = self.create("species", {"name": "Собака"})
        breed = self.create("breeds", {"name": "Лабрадор", "species": species})
        response = self.client.post("/api/pets/", {
            "name": "Буся", "breed": breed, "age_months": -2, "price": "-3",
        }, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()), {"age_months", "price"})
        response = self.client.delete(f"/api/species/{species}/")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get(f"/api/species/{species}/").status_code, 200)

    def test_swagger_describes_bearer_token(self):
        docs = self.client.get("/api/docs/")
        self.assertContains(docs, "swagger-ui")
        response = self.client.get("/api/schema/", HTTP_ACCEPT="application/vnd.oai.openapi+json")
        self.assertEqual(response.status_code, 200)
        schema = response.json()
        self.assertEqual(schema["components"]["securitySchemes"]["jwtAuth"]["scheme"], "bearer")
        self.assertIn({"jwtAuth": []}, schema["paths"]["/api/pets/"]["get"]["security"])
