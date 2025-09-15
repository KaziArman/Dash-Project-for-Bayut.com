# app.py
import re
import time
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from bs4 import BeautifulSoup

# -----------------------------
# Streamlit page configuration
# -----------------------------
st.set_page_config(
    page_title="DAMAC Towers · Bayut Insights",
    page_icon="🏙️",
    layout="wide",
)

st.title("Data Insights From Bayut.com")
st.subheader("Insights of DAMAC Towers by Paramount Hotels and Resorts (Business Bay, Dubai)")
st.caption("Scraped from Bayut listing pages for for-sale and to-rent at DAMAC Towers by Paramount.")

# -----------------------------
# Constants & helpers
# -----------------------------
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) "
        "Gecko/20100101 Firefox/91.0"
    )
}

BASE = "https://www.bayut.com"
SALE_URL = f"{BASE}/for-sale/property/dubai/business-bay/damac-towers-by-paramount-hotels-and-resorts/"
RENT_URL = f"{BASE}/to-rent/property/dubai/business-bay/damac-towers-by-paramount-hotels-and-resorts/"

SCHEMA = [
    "Status", "Price", "Price (raw)", "Location", "Key Words",
    "Bedrooms", "Bedrooms (num)", "Area (sqft)", "Area (raw)", "Agency"
]

def _num_or_none(s: str):
    """Extract numeric float from messy text, else return None."""
    if not s:
        return None
    s = re.sub(r"[^\d.]", "", s)
    try:
        return float(s) if s else None
    except Exception:
        return None

def _first_attr(el, attr, default=""):
    try:
        return el.get(attr, default)
    except Exception:
        return default

def _text(el):
    return el.get_text(" ", strip=True) if el else ""

# -----------------------------
# Parsing & scraping
# -----------------------------
def _parse_card(card, status_label: str) -> dict:
    price_el = card.select_one("span[aria-label='Price']") or card.find("span", string=re.compile(r"AED|د\.إ"))
    price_text = _text(price_el)
    price_num = _num_or_none(price_text)

    beds_el  = card.select_one("span[aria-label='Beds']")
    beds_text = _text(beds_el)
    m_beds = re.search(r"\d+", beds_text)
    beds_num = int(m_beds.group()) if m_beds else None

    area_el = card.select_one("span[aria-label='Area']") or card.find(string=re.compile(r"sqft|ft²", re.I))
    area_text = _text(area_el)
    area_sqft = _num_or_none(area_text)

    title_text = _text(card.select_one("h2[aria-label='Title']") or card.find("h2"))
    loc_text   = _text(card.select_one("div[aria-label='Location']"))

    agency_img = card.select_one("img[title]") or card.select_one("img[alt]")
    agency = _first_attr(agency_img, "title", "") or _first_attr(agency_img, "alt", "")

    return {
        "Status": status_label,
        "Price": price_num,
        "Price (raw)": price_text,
        "Location": loc_text,
        "Key Words": title_text,
        "Bedrooms": beds_text or "N/A",
        "Bedrooms (num)": beds_num if beds_num is not None else "N/A",
        "Area (sqft)": area_sqft,
        "Area (raw)": area_text,
        "Agency": agency,
    }


def _find_cards(soup: BeautifulSoup):
    """
    Try multiple strategies to locate listing cards.
    """
    cards = soup.select("div.d6e81fd0")
    if cards:
        return cards
    # fallback: parents of title nodes
    h2s = soup.select('h2[aria-label="Title"]')
    parents = []
    for h in h2s:
        p = h
        for _ in range(3):
            if p and p.parent:
                p = p.parent
        if p:
            parents.append(p)
    if parents:
        return parents
    # last resort
    return soup.find_all("article") or soup.find_all("div")

def _bayut(url: str, status_label: str):
    """
    Scrape one Bayut page and return list of parsed dicts.
    """
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.content, "html.parser")
    rows, errs = [], 0
    for card in _find_cards(soup):
        try:
            rows.append(_parse_card(card, status_label))
        except Exception:
            errs += 1
            continue
    if len(rows) == 0 and errs > 0:
        st.warning(
            f"No cards parsed from {status_label} URL; {errs} cards failed to parse. "
            "Bayut markup may have changed."
        )
    return rows

@st.cache_data(show_spinner=True, ttl=60*30)
def scrape_status(status: str) -> pd.DataFrame:
    """
    Scrape per-status (Buy or Rent) so UI switching fetches the right URL.
    """
    url = SALE_URL if status == "Buy" else RENT_URL
    data = _bayut(url, status)
    # ensure schema even with zero results
    df = pd.DataFrame(data, columns=SCHEMA)
    for col in SCHEMA:
        if col not in df.columns:
            df[col] = np.nan
    return df[SCHEMA].copy()

# -----------------------------
# Data (scrape both for metrics)
# -----------------------------
with st.spinner("Scraping Bayut…"):
    # scrape both sides for ABS/ARS/ROI
    df_buy  = scrape_status("Buy")
    time.sleep(0.3)  # be polite
    df_rent = scrape_status("Rent")

df_all = pd.concat([df_buy, df_rent], ignore_index=True)

# -----------------------------
# Metrics
# -----------------------------
ABS1 = df_buy["Price"].dropna().mean() if not df_buy.empty else np.nan
ARS1 = df_rent["Price"].dropna().mean() if not df_rent.empty else np.nan
ROI1 = (ARS1 * 12 / ABS1) if (pd.notna(ABS1) and pd.notna(ARS1) and ABS1 > 0) else np.nan

c1, c2, c3 = st.columns(3)
c1.metric("Average Price (Buy)", f"{ABS1:,.0f}" if pd.notna(ABS1) else "—", help="AED")
c2.metric("Average Price (Rent)", f"{ARS1:,.0f}" if pd.notna(ARS1) else "—", help="AED (often monthly/yearly)")
c3.metric("ROI (Rent ÷ Buy, annualized)", f"{ROI1:.2f}×" if pd.notna(ROI1) else "—")

st.divider()

# -----------------------------
# Controls
# -----------------------------
left, right = st.columns([1, 1])

with left:
    status_choice = st.selectbox("Select Status", options=["All", "Buy", "Rent"], index=2)

with right:
    # build choices from all data (so options don't disappear)
    beds_unique = ["All"] + sorted([
        b for b in df_all["Bedrooms"].dropna().unique().tolist() if b != "N/A"
    ])
    bed_choice = st.selectbox("Number of Bedrooms", options=beds_unique, index=0)

# Select frame according to UI
if status_choice == "All":
    df_selected = df_all
elif status_choice == "Buy":
    df_selected = scrape_status("Buy")
else:
    df_selected = scrape_status("Rent")

# Guard empty
if df_selected.empty:
    st.warning(f"No listings found for {status_choice}.")
    st.stop()

# -----------------------------
# Charts
# -----------------------------
def fig_abs_ars():
    # compare ABS vs ARS (uses both)
    x = ["ABS (Buy)", "ARS (Rent)"]
    y = [
        float(ABS1) if pd.notna(ABS1) else 0,
        float(ARS1) if pd.notna(ARS1) else 0,
    ]
    fig = go.Figure(go.Bar(x=x, y=y, hovertext=["Average Buy Price", "Average Rent Price"]))
    fig.update_traces(marker_line_color="rgb(0,0,0)", marker_line_width=1, opacity=0.9)
    fig.update_layout(
        title="ABS & ARS",
        title_x=0.5,
        plot_bgcolor="black",
        paper_bgcolor="black",
        yaxis_title="AED",
        font=dict(color="black")   # 👈 force black font
    )

    return fig

def fig_bed(df_for_plot: pd.DataFrame, status_sel: str, bed_sel: str):
    if df_for_plot.empty:
        return go.Figure()

    if status_sel == "All" and bed_sel == "All":
        groups = df_for_plot["Bedrooms"].value_counts().sort_index()
        x, y = groups.values.tolist(), groups.index.tolist()
        xaxis_title = "Number of Bedrooms"
    elif bed_sel == "All":
        groups = df_for_plot["Bedrooms"].value_counts().sort_index()
        x, y = groups.values.tolist(), groups.index.tolist()
        xaxis_title = f"Number of Bedrooms ({status_sel})"
    elif status_sel == "All":
        a = df_buy[df_buy["Bedrooms"] == bed_sel]["Bedrooms"].count()
        b = df_rent[df_rent["Bedrooms"] == bed_sel]["Bedrooms"].count()
        x, y = [a, b], ["Buy", "Rent"]
        xaxis_title = f"Count of {bed_sel} Bedroom"
    else:
        a = df_for_plot[(df_for_plot["Status"] == status_sel) & (df_for_plot["Bedrooms"] == bed_sel)]["Bedrooms"].count()
        x, y = [a], [status_sel]
        xaxis_title = f"Count of {bed_sel} Bedroom ({status_sel})"

    fig = go.Figure(go.Bar(x=x, y=y, orientation="h"))
    fig.update_traces(marker_line_color="rgb(0,0,0)", marker_line_width=1, opacity=0.9)
    fig.update_layout(
        title="Status vs Bedrooms",
        title_x=0.5,
        plot_bgcolor="black",
        paper_bgcolor="black",
        xaxis_title=xaxis_title,
        font=dict(color="black")   # 👈 force black font
        )

    return fig

g1, g2 = st.columns([1, 2])
with g1:
    st.plotly_chart(fig_abs_ars(), use_container_width=True)
with g2:
    st.plotly_chart(fig_bed(df_selected, status_choice, bed_choice), use_container_width=True)

st.divider()

# -----------------------------
# Data table
# -----------------------------
st.subheader("Listings Table")
st.caption("Sort/filter within the table as needed.")

table_df = df_selected.copy().sort_values(["Status", "Price"], na_position="last")
display_cols = [
    "Status", "Price", "Price (raw)", "Location", "Key Words",
    "Bedrooms", "Area (sqft)", "Area (raw)", "Agency"
]
have_cols = [c for c in display_cols if c in table_df.columns]

st.dataframe(table_df[have_cols], use_container_width=True, height=420)

st.info(
    "Notes:\n"
    "- Bayut can change HTML structure; adjust `_parse_card` selectors if scraping fails.\n"
    "- Rent prices can be monthly or yearly; ROI shown is Rent × 12 / Buy (simplified)."
)
