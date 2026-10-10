import csv
from pathlib import Path
from src.aumovio_pipeline.transformations import map_country

#function to load csv files into the database
def load_csv(file_path: str | Path) -> list[dict[str, str]]:
    with open(file_path, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        return list(reader)
    
#function to load images into the database   
def load_images(connection, rows):
    for row in rows:
        connection.execute(
            """
            INSERT INTO images (
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

    connection.commit()
    
#function to load labels into the database   
def load_labels(connection, rows):
    for row in rows:
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
                row["record_file_name"],
                int(row["timestamp"]),
                row["label_type"],
                float(row["label_size"].replace(",", ".")),
                row["label_coordinates"],
                int(row["version"]),
            ),
        )

    connection.commit()
    
#function to split the rows into two lists, one for images and one for labels   
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

# function to load images into the database with delta insert (insert only if not exists)
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

# function to load labels into the database with delta insert (insert only if not exists)
def load_labels_delta(connection, rows):
    inserted = 0

    for row in rows:
        existing = connection.execute(
            """
            SELECT 1
            FROM labels
            WHERE record_file_name = ?
              AND timestamp = ?
              AND label_coordinates = ?
            LIMIT 1
            """,
            (
                row["record_file_name"],
                int(row["timestamp"]),
                row["label_coordinates"],
            ),
        ).fetchone()

        if existing:
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
                row["record_file_name"],
                int(row["timestamp"]),
                row["label_type"],
                float(row["label_size"].replace(",", ".")),
                row["label_coordinates"],
                int(row["version"]),
            ),
        )

        inserted += 1

    connection.commit()
    return inserted