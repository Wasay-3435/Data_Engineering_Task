from pathlib import Path

from src.aumovio_pipeline.database import connect
from src.aumovio_pipeline.pipeline import run_pipeline

test_db = Path("data/pipeline_test.db")

# Start with a clean test database
if test_db.exists():
    test_db.unlink()

print("=== First pipeline run ===")
run_pipeline(db_path=test_db)

print("\n=== Second pipeline run ===")
run_pipeline(db_path=test_db)

print("\n=== Final database counts ===")
db = connect(test_db)

image_count = db.execute(
    "SELECT COUNT(*) FROM images"
).fetchone()[0]

label_count = db.execute(
    "SELECT COUNT(*) FROM labels"
).fetchone()[0]

print("Images:", image_count)
print("Labels:", label_count)

db.close()
