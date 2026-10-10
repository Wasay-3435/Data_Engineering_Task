import sqlite3
import unittest

from src.aumovio_pipeline.loaders import (
    load_images,
    load_labels,
    load_images_delta,
    load_labels_delta,
)
from src.aumovio_pipeline.database import initialize_database


class TestLoaders(unittest.TestCase):
    def setUp(self):
        # Create a fresh in-memory database for each test
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        initialize_database(self.db, "sql/schema.sql")

        # Insert an image required by the labels' foreign key
        self.db.execute(
            """
            INSERT INTO images (
                record_file_name, timestamp, image_format, image_path, country
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            ("test_image", 10, "v1", "test/path", "DE"),
        )
        self.db.commit()

    def tearDown(self):
        self.db.close()

    def sample_image(self):
        return {
            "record_file_name": "test_image",
            "timestamp": "10",
            "image_format": "v1",
            "image_path": "test/path",
            "country": "Germany",
        }

    def sample_label(self, version=1, label_type="car"):
        return {
            "record_file_name": "test_image",
            "timestamp": "10",
            "label_type": label_type,
            "label_size": "1,0",
            "label_coordinates": '{"x0": 1, "y0": 2}',
            "version": str(version),
        }

    def test_load_images_ignores_existing_image(self):
        inserted = load_images(self.db, [self.sample_image()])
        count = self.db.execute("SELECT COUNT(*) FROM images").fetchone()[0]

        self.assertEqual(inserted, 0)
        self.assertEqual(count, 1)

    def test_load_labels_inserts_new_label(self):
        inserted = load_labels(self.db, [self.sample_label()])
        count = self.db.execute("SELECT COUNT(*) FROM labels").fetchone()[0]

        self.assertEqual(inserted, 1)
        self.assertEqual(count, 1)

    def test_load_labels_delta_updates_newer_version(self):
        load_labels(self.db, [self.sample_label(version=1, label_type="car")])

        inserted = load_labels_delta(
            self.db,
            [self.sample_label(version=2, label_type="motorbyke")],
        )

        label = self.db.execute(
            "SELECT label_type, version FROM labels"
        ).fetchone()

        self.assertEqual(inserted, 0)
        self.assertEqual(label, ("motorbyke", 2))

    def test_load_labels_delta_ignores_older_version(self):
        load_labels(self.db, [self.sample_label(version=2, label_type="motorbyke")])

        load_labels_delta(
            self.db,
            [self.sample_label(version=1, label_type="car")],
        )

        label = self.db.execute(
            "SELECT label_type, version FROM labels"
        ).fetchone()

        self.assertEqual(label, ("motorbyke", 2))

    def test_load_images_delta_inserts_only_missing_images(self):
        rows = [
            self.sample_image(),
            {
                "record_file_name": "new_image",
                "timestamp": "20",
                "image_format": "v1",
                "image_path": "new/path",
                "country": "Hungary",
            },
        ]

        inserted = load_images_delta(self.db, rows)
        count = self.db.execute("SELECT COUNT(*) FROM images").fetchone()[0]

        self.assertEqual(inserted, 1)
        self.assertEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
