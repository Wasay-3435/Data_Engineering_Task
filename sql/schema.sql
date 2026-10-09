
CREATE TABLE IF NOT EXISTS images (
    record_file_name TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    image_format TEXT,
    image_path TEXT,
    country TEXT,
    PRIMARY KEY (record_file_name, timestamp)
);

CREATE TABLE IF NOT EXISTS labels (
    record_file_name TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    label_type TEXT NOT NULL,
    label_size REAL,
    label_coordinates TEXT,
    version INTEGER NOT NULL,
    FOREIGN KEY (record_file_name, timestamp)
        REFERENCES images (record_file_name, timestamp)
);
