import importlib.util
import sys
import types
import unittest
from pathlib import Path

from bson import ObjectId


REPO_ROOT = Path(__file__).resolve().parents[1]
MAIN_PATH = REPO_ROOT / "main.py"


class FakeCursor:
    def __init__(self, documents):
        self.documents = list(documents)

    def sort(self, sort_params):
        for field, direction in reversed(sort_params):
            reverse = direction == -1
            self.documents.sort(key=lambda item: item[field], reverse=reverse)
        return self

    def skip(self, count):
        self.documents = self.documents[count:]
        return self

    def limit(self, count):
        self.documents = self.documents[:count]
        return self

    def __iter__(self):
        return iter(self.documents)


class FakeCollection:
    def __init__(self, documents):
        self.documents = list(documents)

    def find(self, *_args, **_kwargs):
        return FakeCursor(self.documents)


class FakeDatabase:
    def __init__(self, collection):
        self.collection = collection

    def __getitem__(self, name):
        if name != "book_collection":
            raise KeyError(name)
        return self.collection


def load_app_with_documents(documents):
    module_name = "main"
    sys.modules.pop(module_name, None)
    sys.modules["db_connector"] = types.SimpleNamespace(
        get_database_connection=lambda db_name: FakeDatabase(FakeCollection(documents))
    )

    spec = importlib.util.spec_from_file_location(module_name, MAIN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ListBooksPaginationTests(unittest.TestCase):
    def setUp(self):
        self.documents = [
            {
                "_id": ObjectId(),
                "title": f"Book {index}",
                "author": f"Author {index}",
                "year": 2000 + index,
                "rating": float(index % 5) + 0.1,
                "categories": ["fiction"],
            }
            for index in range(12)
        ]

    def test_list_books_uses_default_pagination(self):
        module = load_app_with_documents(self.documents)

        payload = module.list_books(sort_by="year", order="asc", skip=0, limit=10)
        self.assertEqual(len(payload), 10)
        self.assertEqual(payload[0]["title"], "Book 0")
        self.assertEqual(payload[-1]["title"], "Book 9")

    def test_list_books_applies_skip_limit_and_sorting_together(self):
        module = load_app_with_documents(self.documents)

        payload = module.list_books(sort_by="year", order="desc", skip=2, limit=3)
        self.assertEqual([book["title"] for book in payload], ["Book 9", "Book 8", "Book 7"])


if __name__ == "__main__":
    unittest.main()
