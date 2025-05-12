# Project Todo List

- [x] Refactor notebooks into `download.py` and `visualize.py` scripts.
- [x] Ensure the download script saves talk files to a `/conference_talks` directory, checking if files already exist before downloading.
- [x] Extract citation counts for each individual talk.
- [x] Save talk name, speaker, and citation counts for each conference talk to a single, deduplicated Parquet file (e.g., `conference_talks_ALL.parquet`).
  - Script now deduplicates by base filename and avoids redundant downloads (handles `_lang=eng.html` and plain `.html`).
- [ ] Create interactive visualizations in a Streamlit app, similar to what is in the `conference-citations-visualizations.ipynb` notebook.
- [ ] Build `dashboard.py` Streamlit app:
  - [ ] Sidebar controls for citation type (raw/verse-adjusted) and averaging (raw, 2, 3, 6 conference rolling average)
  - [ ] Visualizations page for scripture citation trends with user-selected options
  - [ ] Talks & Speakers Table page with search/filter for speaker, year, and citation breakdown
  - [ ] Use `conference_talks_2025-05.parquet` as the data source 