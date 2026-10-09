from src.aumovio_pipeline.database import connect, initialize_database

db = connect("data/aumovio.db")
initialize_database(db, "sql/schema.sql")

print("Database created and connected successfully.")

tables = db.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
).fetchall()

print("Tables:", tables)

db.close()