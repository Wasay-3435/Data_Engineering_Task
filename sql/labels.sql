CREATE TABLE labels (
    record_file_name VARCHAR(270),
    "timestamp" INT8,
    label_type VARCHAR(20),
    label_size FLOAT8,
    label_coordinates VARCHAR(max),
    "version" INT8
);