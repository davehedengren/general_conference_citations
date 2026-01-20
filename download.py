import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse
from datetime import datetime
import re
import glob
from typing import Optional

# --- Configuration ---
BASE_URL = "https://www.churchofjesuschrist.org/study/general-conference/"
CONFERENCE_LINKS_DIR = 'conference_links'
CONFERENCE_TALKS_DIR = 'conference_talks'
OUTPUT_PARQUET_DIR = '.' # Current directory for the output parquet file
YEAR_RANGE_START = 1971
YEAR_RANGE_END = datetime.now().year # Process up to the current year
MONTHS_TO_SCRAPE = ['04', '10'] # April and October conferences
REQUEST_DELAY_SECONDS = 2

# --- Utility Functions ---

def save_conference_list_html(url, folder_path):
    """Saves HTML content of a conference list page. Returns (filepath, downloaded)."""
    try:
        filename = url.split('/')[-2] + '-' + url.split('/')[-1].split('?')[0] + '.html'
        filepath = os.path.join(folder_path, filename)
        
        # Check if the file already exists
        if os.path.exists(filepath):
            print(f"Conference list HTML already exists, skipping: {filepath}")
            return filepath, False

        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        html_content = response.text
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Conference list HTML saved to {filepath}")
        return filepath, True
    except requests.exceptions.RequestException as e:
        print(f"An error occurred fetching {url}: {e}")
    except Exception as e:
        print(f"An error occurred saving HTML for {url}: {e}")
    return None, False

def save_talk_html(url, folder_path):
    """Saves HTML content of an individual talk page, avoiding duplicate downloads for _lang=eng and plain versions. Returns (filepath, downloaded)."""
    try:
        parts = url.split('/')
        base_filename = parts[-3] + '-' + parts[-2] + '-' + parts[-1].split('?')[0]
        filename_plain = base_filename + '.html'
        filename_lang = base_filename + '_lang=eng.html'
        filepath_plain = os.path.join(folder_path, filename_plain)
        filepath_lang = os.path.join(folder_path, filename_lang)

        # Check if either file already exists
        if os.path.exists(filepath_plain) or os.path.exists(filepath_lang):
            print(f"Talk HTML already exists, skipping: {filepath_plain} or {filepath_lang}")
            return (filepath_lang if os.path.exists(filepath_lang) else filepath_plain), False

        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save as _lang=eng.html if the URL contains lang=eng, otherwise as plain
        if 'lang=eng' in url:
            filepath = filepath_lang
        else:
            filepath = filepath_plain

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Talk HTML saved to {filepath}")
        return filepath, True
    except requests.exceptions.RequestException as e:
        print(f"An error occurred fetching {url}: {e}")
    except Exception as e:
        print(f"An error occurred saving HTML for {url}: {e}")
    return None, False

def parse_conference_links_to_dataframe(html_folder_path):
    """Parses HTML files from conference list pages to extract talk details into a DataFrame."""
    all_talks_list = []
    for filename in os.listdir(html_folder_path):
        if not filename.endswith('.html'):
            continue
        
        filepath = os.path.join(html_folder_path, filename)
        print(f"Processing conference list: {filename}")
        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        year_from_filename = filename.split('-')[0]
        month_from_filename = filename.split('-')[1][:2]

        # Newer conference pages use hashed CSS class names, but the semantic markers below
        # have been stable (e.g., <p class="primaryMeta">Speaker</p>, <p class="title">Title</p>).
        # We'll parse talk tiles by scanning all anchors and filtering to talk URLs.
        anchors = soup.find_all('a', href=True)
        for a in anchors:
            href = a.get('href', '')
            if not isinstance(href, str):
                continue

            m = re.match(r'^/study/general-conference/(\d{4})/(\d{2})/([^/?#]+)', href)
            if not m:
                continue

            year, month, slug = m.groups()

            # Only keep the conference lists we are processing in this file, to avoid cross-links.
            if str(year) != str(year_from_filename) or str(month) != str(month_from_filename):
                continue

            # Session tiles typically have a title but no speaker primaryMeta.
            title_p = a.find('p', class_='title')
            speaker_p = a.find('p', class_='primaryMeta')
            if not title_p or not speaker_p:
                continue

            title = title_p.get_text(strip=True)
            speaker = speaker_p.get_text(strip=True)
            if not title or not speaker:
                continue

            talk_url_suffix = href
            all_talks_list.append({
                'Title': title,
                'Speaker': speaker,
                'URL_Suffix': talk_url_suffix,
                'Full_URL': "https://www.churchofjesuschrist.org" + talk_url_suffix,
                'Year': str(year_from_filename),
                'Month': str(month_from_filename)
            })
    
    return pd.DataFrame(all_talks_list)

def count_scripture_references_from_file(filepath):
    """Counts scripture references in a single HTML talk file."""
    if not filepath or not os.path.exists(filepath):
        print(f"File not found for counting: {filepath}")
        return {'bom': 0, 'dc': 0, 'pgp': 0, 'nt': 0, 'ot': 0}

    with open(filepath, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    html_as_text = str(soup).lower() # Convert to lower for case-insensitive counting
    
    # More specific search strings to avoid false positives
    search_strings_map = {
        'bom': "scriptures/bofm/",
        'dc': "scriptures/dc-testament/dc/",
        'pgp': "scriptures/pgp/",
        'nt': "scriptures/nt/",
        'ot': "scriptures/ot/"
    }
    
    counts = {key: 0 for key in search_strings_map.keys()}
    
    for key, search_str in search_strings_map.items():
        counts[key] = html_as_text.count(search_str.lower())
            
    return counts

# --- Main Execution ---

def get_base_talk_filename(filename):
    """Returns the base filename for a talk, stripping _lang=eng if present."""
    if filename.endswith('_lang=eng.html'):
        return filename[:-len('_lang=eng.html')] + '.html'
    return filename

def _normalize_url_key(url_suffix: str) -> str:
    """Normalize URL suffixes by stripping query params to dedupe lang variants."""
    if not isinstance(url_suffix, str):
        return ''
    return url_suffix.split('?', 1)[0]

def find_latest_parquet(pattern: str = "conference_talks_*.parquet") -> Optional[str]:
    """Find the latest parquet file by modification time in the current directory."""
    candidates = glob.glob(pattern)
    if not candidates:
        return None
    candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return candidates[0]

def main(start_year, end_year, specific_conference=None, merge_into_parquet: Optional[str] = None, output_parquet: Optional[str] = None):
    """
    Main function to download conference lists, individual talks,
    extract scripture citations, and save to a Parquet file.
    """
    print(f"Starting conference citation download process...")
    print(f"Target years: {start_year} - {end_year}")
    if specific_conference:
        print(f"Specific conference: {specific_conference}")

    # Step 1: Download conference list pages
    if not specific_conference:
        print("\n--- Downloading Conference Lists ---")
        for year in range(start_year, end_year + 1):
            for month in MONTHS_TO_SCRAPE:
                conference_url = f"{BASE_URL}{year}/{month}?lang=eng"
                print(f"Fetching conference list for {year}-{month} from {conference_url}")
                _, downloaded = save_conference_list_html(conference_url, CONFERENCE_LINKS_DIR)
                if downloaded:
                    time.sleep(REQUEST_DELAY_SECONDS)
    else: # Handle specific conference (e.g., 2023-10)
        year, month = specific_conference.split('-')
        conference_url = f"{BASE_URL}{year}/{month}?lang=eng"
        print(f"\n--- Downloading Specific Conference List: {specific_conference} ---")
        print(f"Fetching conference list for {year}-{month} from {conference_url}")
        _, downloaded = save_conference_list_html(conference_url, CONFERENCE_LINKS_DIR)
        if downloaded:
            time.sleep(REQUEST_DELAY_SECONDS)


    # Step 2: Parse conference lists to get individual talk URLs
    print("\n--- Parsing Conference Lists for Talk URLs ---")
    if not os.path.exists(CONFERENCE_LINKS_DIR):
        print(f"Directory {CONFERENCE_LINKS_DIR} not found. Please download conference lists first.")
        return

    talks_df = parse_conference_links_to_dataframe(CONFERENCE_LINKS_DIR)
    if talks_df.empty:
        print("No talks found from conference lists. Exiting.")
        return
    
    print(f"Found {len(talks_df)} talks to process.")
    talks_df['Year'] = talks_df['Year'].astype(str) # Ensure Year and Month are strings for filtering
    talks_df['Month'] = talks_df['Month'].astype(str)

    # Filter for specific conference if provided
    if specific_conference:
        year_filter, month_filter = specific_conference.split('-')
        talks_df = talks_df[(talks_df['Year'] == year_filter) & (talks_df['Month'] == month_filter)].copy()
        print(f"Filtered to {len(talks_df)} talks for conference {specific_conference}.")
        if talks_df.empty:
            print(f"No talks found for the specific conference {specific_conference} after filtering. Exiting.")
            return
    
    # Step 3: Download individual talk HTML files
    print("\n--- Downloading Individual Talk HTML ---")
    downloaded_talk_paths = []
    for index, row in talks_df.iterrows():
        talk_url = row['Full_URL']
        if not talk_url.startswith("http"): # Prepend base if it's a relative URL
            talk_url = "https://www.churchofjesuschrist.org" + talk_url
        
        print(f"Downloading talk: {row['Title']} from {talk_url}")
        filepath, downloaded = save_talk_html(talk_url, CONFERENCE_TALKS_DIR)
        downloaded_talk_paths.append(filepath) # Store path even if None (for error handling later)
        if downloaded:
            time.sleep(REQUEST_DELAY_SECONDS)
    
    talks_df['talk_html_filepath'] = downloaded_talk_paths
    
    # Step 4: Count scripture references
    print("\n--- Counting Scripture References ---")
    citation_counts_list = []
    for filepath in talks_df['talk_html_filepath']:
        if filepath: # Only process if a path was successfully obtained
            counts = count_scripture_references_from_file(filepath)
            citation_counts_list.append(counts)
        else:
            # Append default zero counts if download failed for this talk
            citation_counts_list.append({'bom': 0, 'dc': 0, 'pgp': 0, 'nt': 0, 'ot': 0})

    citations_df = pd.DataFrame(citation_counts_list, index=talks_df.index)
    processed_df = pd.concat([talks_df, citations_df], axis=1)

    # Add a 'filename' column similar to the notebook's df2 for consistency if needed
    # This filename is based on the talk's URL suffix
    processed_df['filename'] = processed_df['URL_Suffix'].apply(
        lambda x: x.split('/')[-3] + '-' + x.split('/')[-2] + '-' + x.split('/')[-1].split('?')[0] + ("_lang=eng.html" if 'lang=eng' in x else ".html") if isinstance(x, str) else None
    )

    # Deduplicate: keep only one file per base talk, preferring _lang=eng.html
    processed_df['base_filename'] = processed_df['filename'].apply(get_base_talk_filename)
    processed_df.sort_values(by=['filename'], ascending=[False], inplace=True)  # _lang=eng.html sorts after .html
    processed_df = processed_df.drop_duplicates(subset=['base_filename'], keep='first')
    processed_df = processed_df.drop(columns=['base_filename'])
    print(f"DataFrame shape after deduplication: {processed_df.shape}")

    # Step 5: Save to Parquet (optionally merge into an existing dataset)
    if not processed_df.empty:
        current_date_str = datetime.now().strftime("%Y-%m")

        # Optional merge target can be provided via CLI args or env vars (for Streamlit Cloud / CI)
        merge_into = (merge_into_parquet or "").strip() or os.environ.get("MERGE_INTO_PARQUET", "").strip() or None
        output_path = (output_parquet or "").strip() or os.environ.get("OUTPUT_PARQUET", "").strip() or None

        if not output_path:
            if specific_conference:
                output_filename = f"conference_talks_{specific_conference}.parquet"
            else:
                output_filename = f"conference_talks_{current_date_str}.parquet"
            output_path = os.path.join(OUTPUT_PARQUET_DIR, output_filename)

        if not os.path.exists(OUTPUT_PARQUET_DIR):
            os.makedirs(OUTPUT_PARQUET_DIR)

        # Add a stable URL key for deduplication (strips ?lang=eng etc.)
        processed_df['url_key'] = processed_df['URL_Suffix'].apply(_normalize_url_key)
        processed_df['has_lang_eng'] = processed_df['URL_Suffix'].astype(str).str.contains('lang=eng', na=False)
        processed_df.sort_values(by=['url_key', 'has_lang_eng'], ascending=[True, False], inplace=True)
        processed_df = processed_df.drop_duplicates(subset=['url_key'], keep='first').drop(columns=['has_lang_eng'])

        if merge_into:
            if not os.path.exists(merge_into):
                print(f"\nMERGE_INTO_PARQUET was set but file not found: {merge_into}. Saving without merge.")
                processed_df.drop(columns=['url_key']).to_parquet(output_path)
                print(f"\nSuccessfully saved processed data to {output_path}")
            else:
                print(f"\nMerging new data into existing parquet: {merge_into}")
                existing_df = pd.read_parquet(merge_into)
                if 'URL_Suffix' not in existing_df.columns:
                    print("Existing parquet missing URL_Suffix; cannot safely merge. Saving without merge.")
                    processed_df.drop(columns=['url_key']).to_parquet(output_path)
                    print(f"\nSuccessfully saved processed data to {output_path}")
                else:
                    existing_df = existing_df.copy()
                    existing_df['url_key'] = existing_df['URL_Suffix'].apply(_normalize_url_key)
                    existing_df['has_lang_eng'] = existing_df['URL_Suffix'].astype(str).str.contains('lang=eng', na=False)

                    merged = pd.concat([existing_df, processed_df], ignore_index=True)
                    merged.sort_values(by=['url_key', 'has_lang_eng'], ascending=[True, False], inplace=True)
                    merged = merged.drop_duplicates(subset=['url_key'], keep='first')
                    merged = merged.drop(columns=['url_key', 'has_lang_eng'])

                    merged.to_parquet(output_path)
                    print(f"\nSuccessfully saved merged dataset to {output_path}")
        else:
            processed_df.drop(columns=['url_key']).to_parquet(output_path)
            print(f"\nSuccessfully saved processed data to {output_path}")
    else:
        print("\nNo data to save to Parquet.")

    print("\n--- Download and Processing Complete ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and process General Conference talks.")
    parser.add_argument(
        "--start_year", 
        type=int, 
        default=YEAR_RANGE_START, 
        help=f"The year to start downloading from (inclusive). Default: {YEAR_RANGE_START}"
    )
    parser.add_argument(
        "--end_year", 
        type=int, 
        default=datetime.now().year, 
        help=f"The year to end downloading at (inclusive). Default: current year ({datetime.now().year})"
    )
    parser.add_argument(
        "--specific_conference",
        type=str,
        default=None,
        help="Download a specific conference, e.g., '2023-10'. Overrides start_year and end_year for conference list download but uses them for historical talk processing if no talk data exists."
    )
    parser.add_argument(
        "--merge_into_parquet",
        type=str,
        default=None,
        help="If set, merge newly processed talks into an existing parquet file (deduping by URL), and write the merged result to --output_parquet."
    )
    parser.add_argument(
        "--output_parquet",
        type=str,
        default=None,
        help="Output parquet path. If omitted, defaults to conference_talks_<YYYY-MM>.parquet (or conference_talks_<specific_conference>.parquet)."
    )
    
    args = parser.parse_args()
    
    main(
        start_year=args.start_year,
        end_year=args.end_year,
        specific_conference=args.specific_conference,
        merge_into_parquet=args.merge_into_parquet,
        output_parquet=args.output_parquet
    )