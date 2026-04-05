import streamlit as st
st.set_page_config(layout="wide")
import pandas as pd
import numpy as np
import re
import plotly.graph_objects as go
import plotly.express as px
import os
import glob

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

# --- Custom color palette for scriptures (Set2, colorblind-friendly) ---
SCRIPTURE_COLORS = {
    'Old Testament': px.colors.qualitative.Set2[0],
    'New Testament': px.colors.qualitative.Set2[1],
    'Book of Mormon': px.colors.qualitative.Set2[2],
    'Doctrine and Covenants': px.colors.qualitative.Set2[3],
    'Pearl of Great Price': px.colors.qualitative.Set2[4],
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
    # Prefer an explicit path if provided (Streamlit Cloud secrets/env friendly),
    # otherwise load the newest conference_talks_*.parquet in the repo.
    explicit_path = os.environ.get("CONFERENCE_TALKS_PARQUET", "").strip() or None
    if explicit_path and os.path.exists(explicit_path):
        parquet_path = explicit_path
    else:
        candidates = glob.glob("conference_talks_*.parquet")
        if not candidates:
            st.error("No conference parquet found. Expected a file like conference_talks_YYYY-MM.parquet in the app directory.")
            st.stop()
        candidates.sort(key=lambda p: os.path.getmtime(p), reverse=True)
        parquet_path = candidates[0]

    st.sidebar.caption(f"Data file: `{parquet_path}`")
    df = pd.read_parquet(parquet_path)
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
page = st.sidebar.radio("Go to", ["Visualizations", "Talks & Speakers Table", "Analyses"])

citation_type = st.sidebar.selectbox(
    "Citation Count Type",
    ["Raw citation counts", "Verse-adjusted counts"]
)

smoothing = st.sidebar.selectbox(
    "Averaging",
    ["Raw (no average)", "2-conference rolling average", "3-conference rolling average", "6-conference rolling average"]
)

def _prophet_spans(max_conference: str):
    """Prophet administration spans (YYYY-MM format). End=None means 'through latest conference in dataset'."""
    spans = [
        ("1972-07", "1973-12", "Harold B. Lee", "#66c2a5"),
        ("1973-12", "1985-11", "Spencer W. Kimball", "#fc8d62"),
        ("1985-11", "1994-05", "Ezra Taft Benson", "#8da0cb"),
        ("1994-06", "1995-03", "Howard W. Hunter", "#e78ac3"),
        ("1995-03", "2008-01", "Gordon B. Hinckley", "#a6d854"),
        ("2008-02", "2018-01", "Thomas S. Monson", "#ffd92f"),
        ("2018-01", "2025-09", "Russell M. Nelson", "#e5c494"),
        ("2025-10", None, "Dallin H. Oaks", "#b3b3b3"),
    ]
    out = []
    for start, end, prophet, color in spans:
        out.append((start, end or max_conference, prophet, color))
    return out

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
    max_conf = plot_df['Conference'].max()

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
        fig.add_trace(go.Scatter(x=x_vals, y=plot_df_grouped[col], mode='lines', name=col, line=dict(color=SCRIPTURE_COLORS.get(col))))
    if overlay_prophets:
        # Add prophet spans and offset annotations
        y_offsets = [1.0, 0.92, 0.84, 0.76, 0.68, 0.60, 0.52]  # Fraction of y-axis (top to bottom)
        y_max = plot_df_grouped.max().max()
        for i, (start, end, prophet, color) in enumerate(_prophet_spans(max_conf)):
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
        st.plotly_chart(fig, use_container_width=False, width=1400, height=700)
        st.caption("Each point is a single conference (April or October). Prophet administrations are shown as colored backgrounds.")
    else:
        fig.update_layout(
            xaxis_title="Conference",
            yaxis_title="Number of References",
            legend_title="Scripture",
            title="Scripture Citation Trends",
            margin=dict(l=40, r=40, t=60, b=40)
        )
        st.plotly_chart(fig, use_container_width=False, width=1400, height=700)
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

elif page == "Analyses":
    # ------------------------------------------------------------------
    # Analyses page: one tab per deep-dive analysis under analysis/NN_*/
    # ------------------------------------------------------------------
    ANALYSIS_ROOT = os.path.join(os.path.dirname(__file__), "analysis")

    def _read_md(folder: str) -> str:
        path = os.path.join(ANALYSIS_ROOT, folder, "findings.md")
        if os.path.exists(path):
            with open(path, "r") as f:
                return f.read()
        return "_findings.md not found_"

    def _read_csv(folder: str, name: str) -> pd.DataFrame | None:
        path = os.path.join(ANALYSIS_ROOT, folder, name)
        return pd.read_csv(path) if os.path.exists(path) else None

    st.header("Citation Pattern Analyses")
    st.caption("Twelve exploratory analyses of the citation dataset. "
               "Each tab renders the `findings.md` write-up plus interactive "
               "versions of the supporting tables and charts. "
               "See `analysis/README.md` for the cross-analysis summary.")

    tab_labels = [
        "01 · Curriculum",
        "02 · BoM Challenges",
        "03 · Prophet Fingerprint",
        "04 · Speaker Decomp",
        "05 · Clustering",
        "06 · First Talk",
        "07 · Session Slot",
        "08 · Christ-Centering",
        "09 · Verse-Adjusted",
        "10 · Change Points",
        "11 · Handoff",
        "12 · Diversity",
    ]
    tabs = st.tabs(tab_labels)

    # ----- 01 Curriculum Effect -----
    with tabs[0]:
        st.markdown(_read_md("01_curriculum_effect"))
        st.subheader("Interactive: curriculum-book share over time")
        cs = _read_csv("01_curriculum_effect", "conference_level_shares.csv")
        if cs is not None:
            cs = cs.sort_values(["Year", "Month"])
            cs["Conference"] = cs["Year"].astype(str) + "-" + cs["Month"].astype(str).str.zfill(2)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=cs["Conference"], y=cs["curriculum_book_share"],
                                     mode="lines+markers", name="Share of curriculum book"))
            fig.update_layout(height=400, xaxis_title="Conference",
                              yaxis_title="Share of citations to curriculum book")
            st.plotly_chart(fig, use_container_width=True)
        for name in ("curriculum_lift_2019plus.csv", "curriculum_lift_all_years.csv"):
            d = _read_csv("01_curriculum_effect", name)
            if d is not None:
                st.caption(name)
                st.dataframe(d, use_container_width=True)

    # ----- 02 BoM Challenges -----
    with tabs[1]:
        st.markdown(_read_md("02_bom_challenges"))
        ts = _read_csv("02_bom_challenges", "bom_share_timeseries.csv")
        if ts is not None:
            ts["Conference"] = ts["Year"].astype(str) + "-" + ts["Month"].astype(str).str.zfill(2)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ts["Conference"], y=ts["bom_share"],
                                     mode="lines", name="BoM share", line=dict(color="#66c2a5")))
            # shock markers
            for label, conf in (("Benson 1986-10", "1986-10"),
                                ("Hinckley 2005-10", "2005-10"),
                                ("Nelson 2018-10", "2018-10")):
                fig.add_vline(x=conf, line_dash="dash", line_color="red", opacity=0.5,
                              annotation_text=label, annotation_position="top")
            fig.update_layout(height=420, xaxis_title="Conference", yaxis_title="BoM share")
            st.plotly_chart(fig, use_container_width=True)
        d = _read_csv("02_bom_challenges", "challenge_windows.csv")
        if d is not None:
            st.caption("±4-conference window means")
            st.dataframe(d, use_container_width=True)

    # ----- 03 Prophet Fingerprint -----
    with tabs[2]:
        st.markdown(_read_md("03_prophet_fingerprint"))
        fps = _read_csv("03_prophet_fingerprint", "prophet_fingerprints.csv")
        if fps is not None:
            st.subheader("Pre-presidency personal fingerprints")
            fig = go.Figure()
            for _, row in fps.iterrows():
                fig.add_trace(go.Bar(
                    name=row["prophet"], x=list(BOOK_LABELS.values()),
                    y=[row["bom"], row["dc"], row["pgp"], row["nt"], row["ot"]],
                ))
            fig.update_layout(barmode="group", height=450, yaxis_title="Share",
                              xaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
        sim = _read_csv("03_prophet_fingerprint", "fingerprint_similarity.csv")
        if sim is not None:
            st.dataframe(sim, use_container_width=True)

    # ----- 04 Speaker Decomposition -----
    with tabs[3]:
        st.markdown(_read_md("04_speaker_decomposition"))
        var = _read_csv("04_speaker_decomposition", "variance_decomposition.csv")
        if var is not None:
            st.dataframe(var, use_container_width=True)
        yr = _read_csv("04_speaker_decomposition", "bom_share_by_year.csv")
        if yr is not None:
            fig = px.line(yr, x="Year", y="bom_share", markers=True,
                          title="BoM share of all citations by year",
                          color_discrete_sequence=[SCRIPTURE_COLORS["Book of Mormon"]])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        rl = _read_csv("04_speaker_decomposition", "top_ringleaders.csv")
        if rl is not None:
            st.subheader("Top contributors to the late-era BoM rise")
            fig = px.bar(rl.head(15), x="Speaker", y="contrib_vs_baseline_pp",
                         color="bom_share", color_continuous_scale="Viridis",
                         labels={"contrib_vs_baseline_pp": "Contribution (pp)"})
            fig.update_layout(height=450)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(rl, use_container_width=True)

    # ----- 05 Speaker Clustering -----
    with tabs[4]:
        st.markdown(_read_md("05_speaker_clustering"))
        centers = _read_csv("05_speaker_clustering", "cluster_centers.csv")
        if centers is not None:
            st.subheader("Cluster centers")
            fig = go.Figure()
            for _, r in centers.iterrows():
                fig.add_trace(go.Bar(
                    name=f"Cluster {int(r['cluster'])} (n={int(r['size'])})",
                    x=list(BOOK_LABELS.values()),
                    y=[r["bom"], r["dc"], r["pgp"], r["nt"], r["ot"]],
                ))
            fig.update_layout(barmode="group", height=420, yaxis_title="Normalized share")
            st.plotly_chart(fig, use_container_width=True)
        sp = _read_csv("05_speaker_clustering", "speakers_by_cluster.csv")
        if sp is not None:
            cluster_sel = st.selectbox("Show speakers in cluster:",
                                       sorted(sp["cluster"].unique()))
            st.dataframe(sp[sp["cluster"] == cluster_sel].sort_values("n_talks",
                         ascending=False), use_container_width=True)

    # ----- 06 First Talk -----
    with tabs[5]:
        st.markdown(_read_md("06_first_talk"))
        ft = _read_csv("06_first_talk", "debut_vs_steady_state.csv")
        if ft is not None:
            fig = px.scatter(ft, x="bom_debut", y="bom_rest", hover_name="speaker",
                             size="n_talks", color="cos_debut_vs_rest",
                             color_continuous_scale="RdYlGn",
                             labels={"bom_debut": "BoM share in debut talk",
                                     "bom_rest": "BoM share in later talks"})
            fig.add_shape(type="line", x0=0, y0=0, x1=1, y1=1,
                          line=dict(color="gray", dash="dot"))
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(ft, use_container_width=True)

    # ----- 07 Session Slot -----
    with tabs[6]:
        st.markdown(_read_md("07_session_slot"))
        m = _read_csv("07_session_slot", "by_month.csv")
        if m is not None:
            st.subheader("April vs October")
            st.dataframe(m, use_container_width=True)
        q = _read_csv("07_session_slot", "by_quartile.csv")
        if q is not None:
            st.subheader("Within-conference quartile")
            st.dataframe(q, use_container_width=True)

    # ----- 08 Christ-Centering -----
    with tabs[7]:
        st.markdown(_read_md("08_christ_centering"))
        yr = _read_csv("08_christ_centering", "christ_index_by_year.csv")
        if yr is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=yr["Year"], y=yr["christ_index"],
                                     mode="lines+markers", name="NT + BoM share",
                                     line=dict(color="#8da0cb", width=3)))
            fig.add_trace(go.Scatter(x=yr["Year"], y=yr["bom_share"],
                                     mode="lines", name="BoM",
                                     line=dict(color=SCRIPTURE_COLORS["Book of Mormon"])))
            fig.add_trace(go.Scatter(x=yr["Year"], y=yr["nt_share"],
                                     mode="lines", name="NT",
                                     line=dict(color=SCRIPTURE_COLORS["New Testament"])))
            fig.update_layout(height=450, xaxis_title="Year",
                              yaxis_title="Share of citations",
                              title="Christ-centering index over time")
            st.plotly_chart(fig, use_container_width=True)

    # ----- 09 Verse-Adjusted -----
    with tabs[8]:
        st.markdown(_read_md("09_verse_adjusted_divergence"))

    # ----- 10 Change Points -----
    with tabs[9]:
        st.markdown(_read_md("10_change_points"))
        cp = _read_csv("10_change_points", "change_points.csv")
        if cp is not None:
            book_sel = st.selectbox("Book:", sorted(cp["book"].unique()))
            st.dataframe(cp[cp["book"] == book_sel], use_container_width=True)

    # ----- 11 Handoff -----
    with tabs[10]:
        st.markdown(_read_md("11_prophet_handoff"))
        tr = _read_csv("11_prophet_handoff", "transitions.csv")
        if tr is not None:
            fig = px.bar(tr, x="transition_at", y="delta_pp", color="delta_pp",
                         color_continuous_scale="RdBu_r",
                         hover_data=["outgoing", "incoming"],
                         labels={"delta_pp": "Δ BoM share (pp)"},
                         title="BoM share change across each transition (±8 conferences)")
            fig.update_layout(height=420)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(tr, use_container_width=True)

    # ----- 12 Diversity -----
    with tabs[11]:
        st.markdown(_read_md("12_scripture_diversity"))
        ent = _read_csv("12_scripture_diversity", "entropy_by_year.csv")
        if ent is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ent["Year"], y=ent["mean_talk_entropy"],
                                     mode="lines+markers", name="Mean talk entropy"))
            fig.add_trace(go.Scatter(x=ent["Year"], y=ent["agg_entropy"],
                                     mode="lines+markers", name="Aggregate entropy",
                                     yaxis="y2"))
            fig.update_layout(
                height=450, xaxis_title="Year",
                yaxis=dict(title="Mean per-talk entropy"),
                yaxis2=dict(title="Aggregate entropy", overlaying="y",
                            side="right", range=[1.8, 2.35]),
                title="Per-talk vs aggregate Shannon entropy of citation mix",
            )
            st.plotly_chart(fig, use_container_width=True)