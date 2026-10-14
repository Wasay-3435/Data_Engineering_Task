# AUMOVIO — Data Engineering Assignment

## Overview

This project implements a Python and SQLite data pipeline for processing image metadata and label data from the Papaya and Kumquat datasets.

The pipeline loads CSV files, handles incremental data loading, maintains the latest version of each logical label, and provides SQL queries for image and label analysis.

## Project Structure

```text
Data_Engineering_Task/
├── data/
│   └── raw/
│       ├── papaya_output_images.csv
│       ├── papaya_output_labels.csv
│       └── kumquat_output.csv
├── docs/
│   └── architecture.md
├── sql/
│   ├── analysis.sql
│   ├── images.sql
│   ├── labels.sql
│   └── schema.sql
├── src/
│   └── aumovio_pipeline/
│       ├── database.py
│       ├── loaders.py
│       ├── transformations.py
│       └── pipeline.py
├── tests/
│   ├── test_loaders.py
│   └── test_transformations.py
├── run_pipeline.py
├── run_analysis.py
├── test_database.py
├── test_pipeline_run.py
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.11 or compatible
- Dependencies listed in `requirements.txt`

## Setup

Open a terminal in the project root.

Create and activate a virtual environment on Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Pipeline

Execute:

```powershell
python run_pipeline.py
```

The pipeline initializes the SQLite database, loads the Papaya datasets, processes the combined Kumquat dataset, and applies the label-version handling logic.

The database is created at `data/aumovio.db`.

## Run the SQL Analysis

Execute:

```powershell
python run_analysis.py
```

The SQL analysis contains queries to:

1. Find images without labels.
2. Retrieve the two largest labels per image.
3. Find the image or images with the greatest number of labels whose size is at least `0.6`, including ties.

## Run the Tests

Run the automated unit tests:

```powershell
python -m unittest discover -s tests -v
```

Run the repeat-execution integration check:

```powershell
python test_pipeline_run.py
```

The integration check uses a separate test database to verify that rerunning the pipeline with the same input data does not insert duplicate records.

## Data Processing

- **Image loading:** Existing image records are ignored using the image table's composite primary key.
- **Label versioning:** Labels are identified by image identity and label coordinates. Incoming higher versions replace older versions for the same logical label.
- **Delta loading:** Existing image records are skipped, and labels are inserted or updated according to their versions.
- **Country mapping:** The current implementation maps Germany to `DE` and Hungary to `HU`. These mappings are implementation assumptions because no separate attribute-mapping file was identified in the provided project files.
- **Database integrity:** SQLite foreign-key enforcement is enabled by the database connection helper.

## Notes

Database files and Python virtual-environment files should remain excluded from version control. The input CSV files are retained under `data/raw/`.

## Solution Notes

The `docs/notes/handwritten_solution_notes.pdf` file contains
my handwritten notes documenting my understanding of the task,
the approach taken, and the reasoning behind the solution.

