-- Task 6.1: Find images that have no labels

SELECT i.*
FROM images AS i
WHERE NOT EXISTS (
    SELECT 1
    FROM labels AS l
    WHERE l.record_file_name = i.record_file_name
      AND l.timestamp = i.timestamp
);


-- Task 6.2: Find the two largest labels per image

SELECT *
FROM (
    SELECT
        l.*,
        ROW_NUMBER() OVER (
            PARTITION BY record_file_name, timestamp
            ORDER BY label_size DESC,
                     label_type ASC,
                     label_coordinates ASC
        ) AS row_num
    FROM labels AS l
)
WHERE row_num <= 2
ORDER BY record_file_name, timestamp, row_num;



--Task 6.3: Find image(s) with the most labels of size >= 0.6

WITH qualifying_counts AS (
    SELECT
        record_file_name,
        timestamp,
        COUNT(*) AS label_count
    FROM labels
    WHERE label_size >= 0.6
    GROUP BY record_file_name, timestamp
),
ranked AS (
    SELECT
        record_file_name,
        timestamp,
        label_count,
        MAX(label_count) OVER () AS max_label_count
    FROM qualifying_counts
)
SELECT
    i.record_file_name,
    i.timestamp,
    i.image_format,
    i.image_path,
    i.country,
    r.label_count
FROM ranked AS r
JOIN images AS i
    ON i.record_file_name = r.record_file_name
    AND i.timestamp = r.timestamp
WHERE r.label_count = r.max_label_count
ORDER BY i.record_file_name, i.timestamp;