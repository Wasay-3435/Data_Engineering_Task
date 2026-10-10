import csv
from pathlib import Path

from src.aumovio_pipeline.transformations import map_country


# Load a CSV file and return its rows as dictionaries
def load_csv(file_path: str | Path) -> list[dict[str, str]]:
    with open(file_path, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        return list(reader)


# Load images, ignoring records whose primary key already exists
def load_images(connection, rows):
    inserted = 0

    for row in rows:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO images (
                record_file_name,
                timestamp,
                image_format,
                image_path,
                country
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                row["record_file_name"],
                int(row["timestamp"]),
                row["image_format"],
                row["image_path"],
                map_country(row["country"]),
            ),
        )

        inserted += cursor.rowcount

    connection.commit()
    return inserted


# Load labels: insert missing identities or update when a newer version arrives
def load_labels(connection, rows):
    inserted = 0
    updated = 0

    for row in rows:
        record_file_name = row["record_file_name"]
        timestamp = int(row["timestamp"])
        label_coordinates = row["label_coordinates"]
        incoming_version = int(row["version"])
        label_size = float(row["label_size"].replace(",", "."))

        existing = connection.execute(
            """
            SELECT version
            FROM labels
            WHERE record_file_name = ?
              AND timestamp = ?
              AND label_coordinates = ?
            ORDER BY version DESC
            LIMIT 1
            """,
            (record_file_name, timestamp, label_coordinates),
        ).fetchone()

        if existing:
            current_version = existing[0]

            if incoming_version <= current_version:
                continue

            connection.execute(
                """
                UPDATE labels
                SET label_type = ?,
                    label_size = ?,
                    version = ?
                WHERE record_file_name = ?
                  AND timestamp = ?
                  AND label_coordinates = ?
                """,
                (
                    row["label_type"],
                    label_size,
                    incoming_version,
                    record_file_name,
                    timestamp,
                    label_coordinates,
                ),
            )

            updated += 1
            continue

        connection.execute(
            """
            INSERT INTO labels (
                record_file_name,
                timestamp,
                label_type,
                label_size,
                label_coordinates,
                version
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record_file_name,
                timestamp,
                row["label_type"],
                label_size,
                label_coordinates,
                incoming_version,
            ),
        )

        inserted += 1

    connection.commit()

    print(f"New labels inserted: {inserted}")
    print(f"Existing labels updated: {updated}")

    return inserted


# Split the combined Kumquat rows into image rows and label rows
def split_kumquat_rows(rows):
    image_rows = []
    label_rows = []

    for row in rows:
        image_rows.append({
            "record_file_name": row["record_file_name"],
            "timestamp": row["timestamp"],
            "image_format": row["image_format"],
            "image_path": row["image_path"],
            "country": row["country"],
        })

        label_rows.append({
            "record_file_name": row["record_file_name"],
            "timestamp": row["timestamp"],
            "label_type": row["label_type"],
            "label_size": row["label_size"],
            "label_coordinates": row["label_coordinates"],
            "version": row["version"],
        })

    return image_rows, label_rows


# Insert only new images from the delta dataset
def load_images_delta(connection, rows):
    inserted = 0

    for row in rows:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO images (
                record_file_name,
                timestamp,
                image_format,
                image_path,
                country
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                row["record_file_name"],
                int(row["timestamp"]),
                row["image_format"],
                row["image_path"],
                map_country(row["country"]),
            ),
        )

        inserted += cursor.rowcount

    connection.commit()
    return inserted


# Insert new logical labels or update existing labels if a newer version arrives
def load_labels_delta(connection, rows):
    inserted = 0
    updated = 0

    for row in rows:
        record_file_name = row["record_file_name"]
        timestamp = int(row["timestamp"])
        label_coordinates = row["label_coordinates"]
        incoming_version = int(row["version"])
        label_size = float(row["label_size"].replace(",", "."))

        existing = connection.execute(
            """
            SELECT version
            FROM labels
            WHERE record_file_name = ?
              AND timestamp = ?
              AND label_coordinates = ?
            ORDER BY version DESC
            LIMIT 1
            """,
            (record_file_name, timestamp, label_coordinates),
        ).fetchone()

        if existing:
            current_version = existing[0]

            if incoming_version <= current_version:
                continue

            connection.execute(
                """
                UPDATE labels
                SET label_type = ?,
                    label_size = ?,
                    version = ?
                WHERE record_file_name = ?
                  AND timestamp = ?
                  AND label_coordinates = ?
                """,
                (
                    row["label_type"],
                    label_size,
                    incoming_version,
                    record_file_name,
                    timestamp,
                    label_coordinates,
                ),
            )

            updated += 1
            continue

        connection.execute(
            """
            INSERT INTO labels (
                record_file_name,
                timestamp,
                label_type,
                label_size,
                label_coordinates,
                version
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                record_file_name,
                timestamp,
                row["label_type"],
                label_size,
                label_coordinates,
                incoming_version,
            ),
        )

        inserted += 1

    connection.commit()

    print(f"New Kumquat labels inserted: {inserted}")
    print(f"Existing Kumquat labels updated: {updated}")

    return inserted
