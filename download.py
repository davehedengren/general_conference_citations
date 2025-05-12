import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import argparse
from datetime import datetime

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
        ul_elements = soup.find_all('ul', {'class': 'subItems-iyPWM'}) # Adjusted class name based on common patterns, might need verification
        if not ul_elements: # Try another common class if the first fails
            ul_elements = soup.find_all('ul', {'class': 'subItems_000_subItems'})


        year_from_filename = filename.split('-')[0]
        month_from_filename = filename.split('-')[1][:2]

        for ul in ul_elements:
            for li in ul.find_all('li'):
                a_tag = li.find('a')
                if a_tag and a_tag.has_attr('href'):
                    title_div = a_tag.find('div', {'class': 'itemTitle-MXhtV'}) # Adjusted class name
                    subtitle_p = a_tag.find('p', {'class': 'subtitle-LKtQp'})   # Adjusted class name
                    
                    if title_div and subtitle_p:
                        title = title_div.text.strip()
                        speaker = subtitle_p.text.strip()
                        talk_url_suffix = a_tag['href']
                        
                        all_talks_list.append({
                            'Title': title, 
                            'Speaker': speaker, 
                            'URL_Suffix': talk_url_suffix,
                            'Full_URL': "https://www.churchofjesuschrist.org" + talk_url_suffix,
                            'Year': year_from_filename, 
                            'Month': month_from_filename
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

def main(start_year, end_year, specific_conference=None):
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

    # Step 5: Save to Parquet
    if not processed_df.empty:
        current_date_str = datetime.now().strftime("%Y-%m")
        if specific_conference: # If a specific conference was processed, use its YYYY-MM for filename
            output_filename = f"conference_talks_{specific_conference}.parquet"
        else: # Otherwise, use current month
            output_filename = f"conference_talks_{current_date_str}.parquet"
        
        output_filepath = os.path.join(OUTPUT_PARQUET_DIR, output_filename)
        if not os.path.exists(OUTPUT_PARQUET_DIR):
            os.makedirs(OUTPUT_PARQUET_DIR)
        
        processed_df.to_parquet(output_filepath)
        print(f"\nSuccessfully saved processed data to {output_filepath}")
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
    
    args = parser.parse_args()
    
    main(start_year=args.start_year, end_year=args.end_year, specific_conference=args.specific_conference) 