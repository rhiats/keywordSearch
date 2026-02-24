import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import BytesIO

st.title("🌐 URL Enrichment with Requests")

# Example filtered_df
if "filtered_df" not in st.session_state:
    st.warning("No filtered data found.")
    st.stop()

df = st.session_state["filtered_df"]

if 'url' not in df.columns:
    st.error("No 'url' column found.")
    st.stop()

selected_urls = st.multiselect(
    "Select URLs to enrich",
    options=df['url'].dropna().unique()
)

if not selected_urls:
    st.info("Select URLs to enrich.")
    st.stop()

enrichment_results = []
progress_bar = st.progress(0)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/117.0.0.0 Safari/537.36"
}

for i, url in enumerate(selected_urls):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Title
        title = soup.title.string.strip() if soup.title else "None"

        # Meta description (check multiple tags)
        meta_description = ""
        meta_tags = [
            {"name": "description"},
            {"property": "og:description"},
            {"name": "twitter:description"}
        ]
        for tag in meta_tags:
            meta_tag = soup.find("meta", attrs=tag)
            if meta_tag and meta_tag.get("content"):
                meta_description = meta_tag["content"].strip()
                break
        if not meta_description:
            meta_description = "Not found"

        # H1 headings
        h1_text = " | ".join([h.get_text(strip=True) for h in soup.find_all("h1")]) or "None"

        # All links
        all_links = " | ".join([a.get("href") for a in soup.find_all("a", href=True)]) or "None"

        enrichment_results.append({
            "url": url,
            "title": title,
            "meta_description": meta_description,
            "h1": h1_text,
            "all_links": all_links
        })

    except Exception as e:
        enrichment_results.append({
            "url": url,
            "title": "",
            "meta_description": f"Error: {e}",
            "h1": "",
            "all_links": ""
        })

    progress_bar.progress((i + 1) / len(selected_urls))

# Display results
result_df = pd.DataFrame(enrichment_results)
st.dataframe(result_df)

# Download CSV
output = BytesIO()
result_df.to_csv(output, index=False)
st.download_button(
    "Download Enriched CSV",
    data=output.getvalue(),
    file_name="enriched_urls.csv",
    mime="text/csv"
)