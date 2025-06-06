
import streamlit as st
import requests
from bs4 import BeautifulSoup
import os
from pathlib import Path

st.title("Descargador de imágenes de aves desde iNaturalist")
st.write("Esta herramienta permite descargar imágenes por especie desde iNaturalist.org")

especies = {
    "Tiuque (Milvago chimango)": "Milvago chimango",
    "Queltehue (Vanellus chilensis)": "Vanellus chilensis",
    "Carancho (Caracara plancus)": "Caracara plancus",
    "Cauquén (Chloephaga picta)": "Chloephaga picta"
}

especie_seleccionada = st.selectbox("Selecciona una especie", list(especies.keys()))
cantidad = st.slider("Cantidad de imágenes a descargar", min_value=10, max_value=100, value=50)

if st.button("Iniciar descarga"):
    nombre_especie = especies[especie_seleccionada]
    carpeta_destino = Path("dataset") / nombre_especie.replace(" ", "_")
    carpeta_destino.mkdir(parents=True, exist_ok=True)

    st.write(f"Buscando imágenes para: {nombre_especie}...")

    url = f"https://www.inaturalist.org/taxa/search?q={nombre_especie.replace(' ', '+')}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    taxon_link = soup.find("a", class_="TaxonSearchResult")
    if not taxon_link:
        st.error("No se encontró la especie en iNaturalist.")
    else:
        taxon_url = "https://www.inaturalist.org" + taxon_link["href"] + "/browse_photos"
        r = requests.get(taxon_url)
        soup = BeautifulSoup(r.text, "html.parser")
        img_tags = soup.find_all("img")[:cantidad]

        progreso = st.progress(0)
        for i, img in enumerate(img_tags):
            img_url = img["src"].replace("square", "original")
            ext = img_url.split(".")[-1].split("?")[0]
            img_data = requests.get(img_url).content
            with open(carpeta_destino / f"{nombre_especie.replace(' ', '_')}_{i}.{ext}", "wb") as f:
                f.write(img_data)
            progreso.progress((i + 1) / len(img_tags))

        st.success(f"Descarga completada: {len(img_tags)} imágenes guardadas en {carpeta_destino}")
