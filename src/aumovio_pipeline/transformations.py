def deduplicate_label_versions(connection):
    connection.execute(
        """
        DELETE FROM labels
        WHERE version < (
            SELECT MAX(other.version)
            FROM labels AS other
            WHERE other.record_file_name = labels.record_file_name
              AND other.timestamp = labels.timestamp
              AND other.label_coordinates = labels.label_coordinates
        )
        """
    )

    connection.commit()
    
# Map country names to their corresponding codes  
COUNTRY_MAP = {
    "Germany": "DE",
    "Hungary": "HU",
}


def map_country(country: str) -> str:
    return COUNTRY_MAP.get(country, country)

def update_country_codes(connection):
    for country_name, country_code in COUNTRY_MAP.items():
        connection.execute(
            """
            UPDATE images
            SET country = ?
            WHERE country = ?
            """,
            (country_code, country_name),
        )

    connection.commit()