from src.aumovio_pipeline.database import connect, initialize_database
from src.aumovio_pipeline.loaders import load_csv, load_images, load_labels

db = connect("data/aumovio.db")
initialize_database(db, "sql/schema.sql")

# Read the Papaya CSV files
images = load_csv("data/raw/papaya_output_images.csv")
labels = load_csv("data/raw/papaya_output_labels.csv")

# Insert records into the database
load_images(db, images)
load_labels(db, labels)

# Verify the stored records
print("Images:", db.execute("SELECT COUNT(*) FROM images").fetchone()[0])
print("Labels:", db.execute("SELECT COUNT(*) FROM labels").fetchone()[0])

db.close()