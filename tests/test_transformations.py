import sqlite3
import unittest

from src.aumovio_pipeline.database import initialize_database
from src.aumovio_pipeline.transformations import (
    map_country,
    update_country_codes,
    deduplicate_label_versions,
)


class TestTransformations(unittest.TestCase):
    def setUp(self):
        # Create a fresh in-memory database for each test
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys = ON")
        initialize_database(self.db, "sql/schema.sql")

    def tearDown(self):
        self.db.close()

    def test_map_country(self):
        self.assertEqual(map_country("Germany"), "DE")
        self.assertEqual(map_country("Hungary"), "HU")

    def test_map_unknown_country(self):
        # Unknown countries are returned unchanged
        self.assertEqual(map_country("France"), "France")

    def test_update_country_codes(self):
        self.db.executemany(
            """
            INSERT INTO images (
                record_file_name, timestamp, image_format, image_path, country
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                ("image_germany", 1, "v1", "path/1", "Germany"),
                ("image_hungary", 2, "v1", "path/2", "Hungary"),
            ],
        )
        self.db.commit()

        update_country_codes(self.db)

        countries = self.db.execute(
            "SELECT country FROM images ORDER BY record_file_name"
        ).fetchall()

        self.assertEqual(countries, [("DE",), ("HU",)])

    def test_deduplicate_label_versions(self):
        self.db.execute(
            """
            INSERT INTO images (
                record_file_name, timestamp, image_format, image_path, country
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            ("test_image", 10, "v1", "test/path", "DE"),
        )

        coordinates = '{"x0": 1, "y0": 2}'

        self.db.executemany(
            """
            INSERT INTO labels (
                record_file_name, timestamp, label_type, label_size,
                label_coordinates, version
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                ("test_image", 10, "car", 1.0, coordinates, 1),
                ("test_image", 10, "motorbyke", 2.0, coordinates, 2),
            ],
        )
        self.db.commit()

        deduplicate_label_versions(self.db)

        labels = self.db.execute(
            """
            SELECT label_type, version
            FROM labels
            WHERE record_file_name = ?
              AND timestamp = ?
              AND label_coordinates = ?
            """,
            ("test_image", 10, coordinates),
        ).fetchall()

        self.assertEqual(labels, [("motorbyke", 2)])


if __name__ == "__main__":
    unittest.main()
