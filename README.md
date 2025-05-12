# Conference Citations Project

This project downloads and analyzes General Conference talks from The Church of Jesus Christ of Latter-day Saints, measuring citation patterns of scriptural works within these talks.

## Project Overview

The project consists of two main components:

1.  **Data Download & Processing**:
    *   The `download.py` script fetches conference talk data from the official website.
    *   It scrapes main conference pages for each year/month, saving them in the `conference_links/` directory.
    *   Individual talk HTML files are downloaded to the `conference_talks/` directory, with deduplication to avoid redundant downloads (handles language variants).
    *   The script extracts metadata (Title, Speaker, Year, Month, etc.) and counts references to different books of scripture (Book of Mormon, Doctrine and Covenants, Pearl of Great Price, New Testament, Old Testament).
    *   Both raw and verse-adjusted citation counts are computed.
    *   All data is saved to a single Parquet file (e.g., `conference_talks_2025-05.parquet`).

2.  **Data Visualization**:
    *   The `dashboard.py` Streamlit app provides interactive visualizations and tables.
    *   Users can explore citation trends by scripture, apply rolling averages, and view verse-adjusted counts.
    *   The dashboard includes overlays for prophet administrations, making it easy to see trends during different leadership periods.
    *   A searchable table allows users to filter by speaker, year, and see citation breakdowns for each talk.

## Usage

1. **Download and Process Data:**
   ```bash
   python download.py
   ```
   This will populate `/conference_links/`, `/conference_talks/`, and create a Parquet file with all processed data.

2. **Run the Dashboard:**
   ```bash
   streamlit run dashboard.py
   ```
   This launches the interactive dashboard in your browser.

## Data & Version Control
- The `.gitignore` excludes all `.ipynb` files, everything in `/conference_links/` and `/conference_talks/`, and `todo.md` to keep the repository clean.
- All persistent data is stored in Parquet format for efficient analysis.

## Future Development
See `todo.md` for planned enhancements and refactoring tasks. 