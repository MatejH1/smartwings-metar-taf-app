import streamlit as st
from bs4 import BeautifulSoup
import re

def highlight_dangers(code):
    danger_terms = {
        "TSRA": "#ff0000",
        "CB": "#ff0000",
        "RA": "#ff8000",
        "SN": "#a0a0ff",
        "FZ": "#ff00ff",
        "FG": "#aaaaaa",
        "+": "#ff0033",
        "WS": "#cc00ff",
    }

    wind_match = re.search(r'(\d{3})(\d{2,3})G?(\d{2,3})?KT', code)
    if wind_match:
        speed = int(wind_match.group(2))
        gust = int(wind_match.group(3)) if wind_match.group(3) else 0
        if speed > 30 or gust > 30:
            code = code.replace(wind_match.group(0), f'<span style="color:#ff9900;font-weight:bold;">{wind_match.group(0)}</span>')

    vis_match = re.search(r'(\s|^)(\d{4})(\s|$)', code)
    if vis_match:
        vis_val = int(vis_match.group(2))
        if vis_val < 1000:
            code = code.replace(vis_match.group(2), f'<span style="color:#00ffff;font-weight:bold;">{vis_match.group(2)}</span>')

    code = re.sub(r'(BKN)(\d{3})', lambda m: f'<span style="color:#ff6600;font-weight:bold;">{m.group(0)}</span>' if int(m.group(2).lstrip("0") or "0") <= 5 else m.group(0), code)

    for term, color in danger_terms.items():
        code = re.sub(fr'\+?{term}', lambda m: f'<span style="color:{color};font-weight:bold;">{m.group(0)}</span>', code, flags=re.IGNORECASE)

    return code

def process_metar_taf(soup):
    output_html = "<h2>Výstup:</h2>"
    for taf_block in soup.select("table.metar-taf"):
        try:
            airport_code = taf_block.select_one("strong").text.strip()
            metar_code = taf_block.select("code")[0].text.strip()
            taf_code = taf_block.select("code")[1].text.strip()

            metar_highlighted = highlight_dangers(metar_code)
            taf_highlighted = highlight_dangers(taf_code)

            output_html += f"<h3>{airport_code}</h3>"
            output_html += f"<p><strong>METAR:</strong> {metar_highlighted}</p>"
            output_html += f"<p><strong>TAF:</strong> {taf_highlighted}</p>"
        except Exception as e:
            output_html += f"<p><i>Chyba: {e}</i></p>"
    return output_html

st.set_page_config(page_title="Vyhodnocení METAR/TAF", layout="centered")
st.title("Vyhodnocení METAR/TAF")

uploaded_file = st.file_uploader("Nahraj HTML soubor s METAR/TAF", type=["html", "htm"])

if uploaded_file is not None:
    file_content = uploaded_file.read()
    soup = BeautifulSoup(file_content, "html.parser")
    output_html = process_metar_taf(soup)
    st.markdown(output_html, unsafe_allow_html=True)
