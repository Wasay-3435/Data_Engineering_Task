from pathlib import Path

from src.aumovio_pipeline.database import connect

db = connect("data/aumovio.db")

sql_text = Path("sql/analysis.sql").read_text(encoding="utf-8")

queries = sql_text.split(";")

for query in queries:
    query = query.strip()

    if not query:
        continue

    print("\n" + "=" * 60)
    print(query.splitlines()[0])
    print("=" * 60)

    results = db.execute(query).fetchall()

    for row in results:
        print(row)

db.close()