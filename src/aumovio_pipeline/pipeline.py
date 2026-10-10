from pathlib import Path

from src.aumovio_pipeline.database import connect, initialize_database
from src.aumovio_pipeline.loaders import (
    load_csv,
    load_images,
    load_labels,
    split_kumquat_rows,
    load_images_delta,
    load_labels_delta,
)
from src.aumovio_pipeline.transformations import deduplicate_label_versions


def run_pipeline(
    data_dir: str | Path = "data/raw",
    db_path: str | Path = "data/aumovio.db",
    schema_path: str | Path = "sql/schema.sql",
) -> None:
    """Load Papaya and Kumquat data, then apply transformations."""

    data_dir = Path(data_dir)
    connection = connect(db_path)

    try:
        # 1. Initialize database tables
        initialize_database(connection, schema_path)

        # 2. Read Papaya data
        papaya_images = load_csv(data_dir / "papaya_output_images.csv")
        papaya_labels = load_csv(data_dir / "papaya_output_labels.csv")

        # 3. Load Papaya data
        papaya_images_inserted = load_images(connection, papaya_images)
        papaya_labels_inserted = load_labels(connection, papaya_labels)

        # 4. Read and split Kumquat data
        kumquat_rows = load_csv(data_dir / "kumquat_output.csv")
        kumquat_images, kumquat_labels = split_kumquat_rows(kumquat_rows)

        # 5. Deduplicate existing labels before delta loading
        deduplicate_label_versions(connection)

        # 6. Insert only new Kumquat images
        images_inserted = load_images_delta(connection, kumquat_images)

        # 7. Insert new labels or update existing labels if a newer version arrives
        labels_inserted = load_labels_delta(connection, kumquat_labels)

        # 8. Deduplicate again after delta loading
        deduplicate_label_versions(connection)

        # 9. Report insertion counts
        print("Pipeline completed successfully.")
        print(f"New Papaya images inserted: {papaya_images_inserted}")
        print(f"Papaya labels loaded: {papaya_labels_inserted}")
        print(f"New Kumquat images inserted: {images_inserted}")
        print(f"New Kumquat labels inserted: {labels_inserted}")

    finally:
        connection.close()
