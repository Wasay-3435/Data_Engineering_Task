import csv
from pathlib import Path

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
                row["country"],
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