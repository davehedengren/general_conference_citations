import streamlit as st
import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go

# --- Verse counts for each book ---
VERSE_COUNTS = {
    'ot': 23145,
    'nt': 7957,
    'bom': 6604,
    'dc': 3654,
    'pgp': 635
}

# --- Readable names for display ---
BOOK_LABELS = {
    'ot': 'Old Testament',
    'nt': 'New Testament',
    'bom': 'Book of Mormon',
    'dc': 'Doctrine and Covenants',
    'pgp': 'Pearl of Great Price'
}

# --- Data Cleaning Helpers ---
def clean_text(text):
    if pd.isnull(text):
        return text
    # Remove common odd special characters and non-ASCII
    text = re.sub(r'[Ââ€™"''–—€©™]', '', text)
    text = re.sub(r'[^\x00-\x7F]+', '', text)  # Remove non-ASCII
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def remove_speaker_from_title(title, speaker):
    if pd.isnull(title) or pd.isnull(speaker):
        return title
    # Remove speaker name from end of title (case-insensitive, ignore whitespace/special chars)
    t = re.sub(r'[^a-zA-Z0-9]', '', title).lower()
    s = re.sub(r'[^a-zA-Z0-9]', '', speaker).lower()
    if t.endswith(s):
        # Remove speaker from end
        return title[:-(len(speaker))].strip()
    return title

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_parquet('conference_talks_2025-05.parquet')
    # Clean up Title and Speaker columns
    df['Speaker'] = df['Speaker'].apply(clean_text)
    df['Title'] = [remove_speaker_from_title(clean_text(t), s) for t, s in zip(df['Title'], df['Speaker'])]
    df['Title'] = df['Title'].apply(clean_text)
    # Add per-100-verse columns
    for col, verses in VERSE_COUNTS.items():
        if col in df.columns:
            df[col + '_per100'] = df[col] / verses * 100
    return df

df = load_data()

# --- Sidebar Controls ---
st.sidebar.title("Conference Citations Dashboard")
page = st.sidebar.radio("Go to", ["Visualizations", "Talks & Speakers Table"])

citation_type = st.sidebar.selectbox(
    "Citation Count Type",
    ["Raw citation counts", "Verse-adjusted counts"]
)

smoothing = st.sidebar.selectbox(
    "Averaging",
    ["Raw (no average)", "2-conference rolling average", "3-conference rolling average", "6-conference rolling average"]
)

# Prophet administration spans (YYYY-MM format)
PROPHET_SPANS = [
    ("1972-07", "1973-12", "Harold B. Lee", "#66c2a5"),
    ("1973-12", "1985-11", "Spencer W. Kimball", "#fc8d62"),
    ("1985-11", "1994-05", "Ezra Taft Benson", "#8da0cb"),
    ("1994-06", "1995-03", "Howard W. Hunter", "#e78ac3"),
    ("1995-03", "2008-01", "Gordon B. Hinckley", "#a6d854"),
    ("2008-02", "2018-01", "Thomas S. Monson", "#ffd92f"),
    ("2018-01", "2025-10", "Russell M. Nelson", "#e5c494"),
]

# --- Helper Functions ---
def get_citation_columns():
    return list(VERSE_COUNTS.keys())

def get_display_labels(cols):
    return [BOOK_LABELS.get(c.replace('_per100', ''), c) for c in cols]

def apply_rolling(df, window):
    group_cols = ["Year", "Month"]
    df_sorted = df.sort_values(group_cols)
    for col in get_citation_columns():
        df_sorted[col + f'_avg{window}'] = df_sorted[col].rolling(window, min_periods=1).mean()
    return df_sorted

# --- Main Area ---
if page == "Visualizations":
    st.header("Scripture Citation Trends")
    overlay_prophets = st.sidebar.checkbox("Overlay Prophet Administrations")
    # Choose columns based on citation type
    if citation_type == "Raw citation counts":
        cols = get_citation_columns()
        plot_df = df.copy()
    else:
        cols = [c + "_per100" for c in get_citation_columns()]
        plot_df = df.copy()
        if not all(col in plot_df.columns for col in cols):
            st.warning("Verse-adjusted counts not available, showing raw counts.")
            cols = get_citation_columns()
        else:
            st.info("This view shows the number of conference citations per 100 verses in each book of scripture.")

    # Create Conference column (YYYY-MM)
    plot_df['Conference'] = plot_df['Year'].astype(str) + '-' + plot_df['Month'].astype(str).str.zfill(2)
    plot_df = plot_df.sort_values(['Year', 'Month'])

    # Smoothing
    if smoothing == "Raw (no average)":
        plot_df_grouped = plot_df.groupby(["Conference"])[cols].sum().reset_index()
    else:
        window = int(smoothing.split('-')[0])
        plot_df_grouped = plot_df.groupby(["Conference"])[cols].sum().reset_index()
        for col in cols:
            plot_df_grouped[col] = plot_df_grouped[col].rolling(window, min_periods=1).mean()

    # Plot with readable labels
    plot_df_grouped = plot_df_grouped.rename(columns={c: l for c, l in zip(cols, get_display_labels(cols))})
    plot_df_grouped = plot_df_grouped.set_index("Conference")

    # Always use Plotly for the main chart
    fig = go.Figure()
    x_vals = plot_df_grouped.index.tolist()
    for col in get_display_labels(cols):
        fig.add_trace(go.Scatter(x=x_vals, y=plot_df_grouped[col], mode='lines', name=col))
    if overlay_prophets:
        # Add prophet spans and offset annotations
        y_offsets = [1.0, 0.92, 0.84, 0.76, 0.68, 0.60, 0.52]  # Fraction of y-axis (top to bottom)
        y_max = plot_df_grouped.max().max()
        for i, (start, end, prophet, color) in enumerate(PROPHET_SPANS):
            fig.add_vrect(
                x0=start, x1=end,
                fillcolor=color, opacity=0.15, line_width=0
            )
            # Offset annotation
            y_pos = y_max * y_offsets[i % len(y_offsets)]
            fig.add_annotation(
                x=start,
                y=y_pos,
                text=prophet,
                showarrow=False,
                font=dict(size=14, color='black'),
                bgcolor='rgba(255,255,255,0.7)',
                bordercolor=color,
                borderpad=2,
                borderwidth=1,
                xanchor='left',
                yanchor='top'
            )
        fig.update_layout(
            xaxis_title="Conference",
            yaxis_title="Number of References",
            legend_title="Scripture",
            title="Scripture Citation Trends with Prophet Administrations",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig, use_container_width=True, height=700)
        st.caption("Each point is a single conference (April or October). Prophet administrations are shown as colored backgrounds.")
    else:
        fig.update_layout(
            xaxis_title="Conference",
            yaxis_title="Number of References",
            legend_title="Scripture",
            title="Scripture Citation Trends",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig, use_container_width=True, height=700)
        st.caption("Each point is a single conference (April or October). Use the sidebar to change citation type and averaging window.")

elif page == "Talks & Speakers Table":
    st.header("Talks & Speakers Table")
    # Speaker dropdown
    speakers = ["All"] + sorted(df["Speaker"].dropna().unique())
    speaker = st.selectbox("Select Speaker:", options=speakers, index=0)
    year = st.selectbox("Filter by Year:", options=["All"] + sorted(df["Year"].unique().astype(str)), index=0)
    
    filtered = df.copy()
    if speaker != "All":
        filtered = filtered[filtered["Speaker"] == speaker]
    if year != "All":
        filtered = filtered[filtered["Year"].astype(str) == year]
    
    # Show both raw and verse-adjusted columns with readable names
    table_cols = get_citation_columns() + [c + '_per100' for c in get_citation_columns()]
    display_cols = [BOOK_LABELS[c] for c in get_citation_columns()] + [BOOK_LABELS[c] + ' (per 100 verses)' for c in get_citation_columns()]
    show_cols = ["Year", "Month", "Title", "Speaker"] + table_cols
    show_display_cols = ["Year", "Month", "Title", "Speaker"] + display_cols
    table = filtered[show_cols].copy()
    table.columns = show_display_cols
    st.dataframe(table)
    st.caption("Search for a speaker or filter by year to see citation breakdowns. All columns are shown with readable names.")

    # If a specific speaker is selected, plot their citation counts by year
    if speaker != "All" and not filtered.empty:
        st.subheader(f"Citation Trends for {speaker}")
        speaker_grouped = filtered.groupby("Year")[get_citation_columns()].sum().reset_index()
        speaker_grouped = speaker_grouped.rename(columns=BOOK_LABELS)
        st.line_chart(speaker_grouped.set_index("Year")[list(BOOK_LABELS.values())]) 