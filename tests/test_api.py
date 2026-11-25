"""Запросы FastAPI к настоящему файлу SQLite."""

import tempfile
import unittest
from pathlib import Path

from alembic import command
from fastapi.testclient import TestClient

from lab7_app.api import create_app

from .support import migration_config


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        workspace = tempfile.TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.database = Path(workspace.name) / "catalog.sqlite3"
        command.upgrade(migration_config(self.database), "head")
        self.client = self.enterContext(TestClient(create_app(self.database)))

    def test_full_crud(self) -> None:
        self.assertEqual(self.client.get("/books").json(), [])
        data = {
            "title": "Евгений Онегин", "author": "Александр Пушкин",
            "year": 1833,
        }
        created = self.client.post("/books", json=data)
        self.assertEqual(created.status_code, 201, created.text)
        resource = created.headers["Location"]
        self.assertEqual(self.client.get(resource).json(), created.json())
        self.assertEqual(self.client.get("/books").json(), [created.json()])

        data["title"] = "Евгений Онегин. Роман в стихах"
        data.pop("year")
        replaced = self.client.put(resource, json=data)
        self.assertEqual(replaced.status_code, 200, replaced.text)
        self.assertIsNone(replaced.json()["year"])
        self.assertEqual(self.client.get(resource).json(), replaced.json())

        deleted = self.client.delete(resource)
        self.assertEqual(deleted.status_code, 204)
        self.assertEqual(deleted.content, b"")
        self.assertEqual(self.client.get(resource).status_code, 404)
        self.assertEqual(self.client.delete(resource).status_code, 404)
        self.assertEqual(self.client.put(resource, json=data).status_code, 404)

    def test_pagination_is_stable_and_invalid_ranges_are_rejected(self) -> None:
        for title in ("Первая", "Вторая", "Третья"):
            response = self.client.post(
                "/books", json={"title": title, "author": "Автор"}
            )
            self.assertEqual(response.status_code, 201)
        results = self.client.get("/books", params={"offset": 1, "limit": 1})
        self.assertEqual(
            [book["title"] for book in results.json()], ["Вторая"]
        )
        for url in (
            "/books?limit=101", "/books?offset=-1", "/books/0",
            "/books/9223372036854775808",
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 422)

    def test_rejected_body_does_not_add_a_row(self) -> None:
        for values in (
            {"title": "  "}, {"author": "a" * 101}, {"year": True},
            {"year": "2024"}, {"year": 2101}, {"unused": "field"},
        ):
            with self.subTest(values=values):
                data = {"title": "Книга", "author": "Автор", **values}
                response = self.client.post("/books", json=data)
                self.assertEqual(response.status_code, 422)
        self.assertEqual(self.client.get("/books").json(), [])

    def test_books_persist_when_api_reopens_database(self) -> None:
        created = self.client.post(
            "/books", json={"title": "  Тихий Дон ", "author": "Шолохов"}
        )
        self.assertEqual(created.status_code, 201)
        self.assertEqual(created.json()["title"], "Тихий Дон")
        with TestClient(create_app(self.database)) as reopened:
            self.assertEqual(reopened.get("/books").json(), [created.json()])
