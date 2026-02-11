import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.request
import json

# Konfiguracja strony
st.set_page_config(page_title="Kalkulator 2026", layout="centered")

# BAZA GATUNKOW
GATUNKI_DATA = {
    "S235JR+N": (9, 24), "S355J2+N": (47, 57), "S355J2+AR": (42, 52), "S355MC": (33, 48), "S700MC": (165, 165), 
    "S355J2C+N CAT-A": (47, 57), "S355K2+N": (62, 62), "S355J2W+N": (175, 175),
    "S420MC Ams": (25, 68), "S500MC-CAT A": (30, 83),
    "S550MC-CAT A": (40, 103), "P265GH": (36, 36),
    "P240NB+N": (39, 39), "P310NB+N": (57, 57), "P355NL1": (101, 101),
    "S355J0WP": (135, 135), "S355J2W": (180, 180), "P355NB+N": (67, 67),
    "30MNB5": (137, 137), "S235J2+N": (24, 24),
    "S235JRCU+N": (34, 49), "S355J2CU+N": (35, 82), "DD11": (2, 2),
    "16MO3": (176, 176)
}

@st.cache_data(ttl=3600)  # Pobieraj kurs raz na godzine
def get_nbp_euro():
    try:
        url = "https://api.nbp.pl/api/exchangerates/rates/a/eur/?format=json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data['rates'][0]['mid']
    except:
        return 4.35

def get_wymiar_extra(t, w):
    if w <= 1550:
        if 3.00 <= t <= 3.99: return 19
        if 4.00 <= t <= 6.99: return 17
        if 7.00 <= t <= 9.99: return 22
        if 10.00 <= t <= 11.99: return 23
        if 12.00 <= t <= 14.99: return 25
        if 15.00 <= t <= 19.99: return 30
        if 20.00 <= t <= 25.99: return 40
        return 25
    else:
        if 3.00 <= t <= 3.99: return 28
        if 4.00 <= t <= 7.99: return 28
        if 8.00 <= t <= 11.99: return 28
        if 12.00 <= t <= 14.99: return 30
        if 15.00 <= t <= 19.99: return 35
        if 20.00 <= t <= 25.99: return 35
        return 35

# UI - NAGLOWEK
st.title("Kalkulator 2026")
kurs = get_nbp_euro()
st.write(f"Aktualny kurs EUR (NBP): **{kurs} PLN**")

# INPUTY
col1, col2 = st.columns(2)
with col1:
    baza = st.number_input("Baza (EUR/t)", value=655.0, step=4.0)
    marza = st.number_input("Baza (EUR/t)", value=35.0, step=1.0)
    gatunek = st.selectbox("Gatunek", list(GATUNKI_DATA.keys()))
with col2:
    t = st.number_input("Grubosc (mm)", value=4.0, step=1.0)
    w = st.number_input("Szerokosc (mm)", value=1500.0, step=100.0)
    l = st.number_input("Dlugosc (mm)", value=6000.0, step=100.0)

# OBLICZENIA
idx = 1 if w > 1550 else 0
e_gat = GATUNKI_DATA[gatunek][idx]
e_wym = get_wymiar_extra(t, w)
total_eur = baza + e_gat + e_wym + marza + 43 + 5
total_pln = total_eur * kurs
waga = (t * w * l * 7.85) / 1_000_000

# WYNIKI
st.divider()
st.subheader(f"Wynik dla: {gatunek} {t}x{w}x{l}")

res_col1, res_col2 = st.columns(2)
res_col1.metric("Cena EUR/t", f"{total_eur:.2f} €")
res_col2.metric("Cena PLN/t", f"{total_pln:.2f} PLN")

st.info(f"Waga arkusza: **{waga:.2f} kg** | Wartość arkusza: **{total_eur*(waga/1000):.2f} EUR**")

# EKSTRAKTY W TABELI
with st.expander("Zobacz szczegóły dopłat"):
    st.write(f"- Ekstrakt Gatunek: {e_gat} EUR")
    st.write(f"- Ekstrakt Wymiar: {e_wym} EUR")
    st.write("- Dodatki stale (Cięcie (43)/Atest(5)/Marża(35)/): 83 EUR")

# OFERTA
if st.button("Dodaj do listy ofert"):
    linia = f"{t}x{w}x{l} {gatunek} - {total_eur:.2f} EUR / {total_pln:.2f} PLN"

    if 'oferty' not in st.session_state:
        st.session_state.oferty = []

    st.session_state.oferty.append(linia)
    st.success("Dodano!")

if 'oferty' in st.session_state and st.session_state.oferty:
    st.write("### Twoje dzisiejsze wyceny:")
    for o in reversed(st.session_state.oferty):
        st.code(o)











