import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import tempfile
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Web SIG Aceh Online", layout="wide")

st.title("🗺️ Web SIG Provinsi Aceh (Online via HP)")
st.write("Aplikasi analisis spasial Shapefile menggunakan Streamlit Cloud.")
st.info("💡 **Petunjuk:** Silakan upload file peta (.shp, .shx, .dbf, .prj, dll) secara bersamaan pada kotak di bawah ini.")

file_diunggah = st.file_uploader(
    "Pilih & Upload file bersamaan:",
    type=["shp", "shx", "dbf", "prj", "cpg", "xml", "sbn", "sbx"],
    accept_multiple_files=True
)

if file_diunggah and len(file_diunggah) >= 4:
    with tempfile.TemporaryDirectory() as folder_sementara:
        jalur_shp = None
        for file in file_diunggah:
            jalur_file = os.path.join(folder_sementara, file.name)
            with open(jalur_file, "wb") as f:
                f.write(file.getbuffer())
            if file.name.endswith(".shp"):
                jalur_shp = jalur_file

        if jalur_shp:
            with st.spinner("Sedang membaca data spasial..."):
                try:
                    gdf = gpd.read_file(jalur_shp)
                    if gdf.crs is None:
                        gdf.set_crs(epsg=4326, inplace=True)
                    elif gdf.crs.to_string() != "EPSG:4326":
                        gdf = gdf.to_crs(epsg=4326)

                    kolom_atribut = [col for col in gdf.columns if col != "geometry"]

                    st.sidebar.header("⚙️ Pengaturan Peta")
                    pilihan_kolom = st.sidebar.selectbox("Pilih Kolom Data Atribut:", options=kolom_atribut)
                    pilihan_tema = st.sidebar.selectbox("Pilih Tema Warna Peta Statis:", options=["YlOrRd", "viridis", "plasma", "magma", "coolwarm"])
                    
                    st.sidebar.markdown("---")
                    st.sidebar.header("🔍 Fitur Pencarian")
                    if "DESA_KEL_1" in gdf.columns:
                        cari_desa = st.sidebar.text_input("Cari Nama Desa/Kelurahan:")
                        if cari_desa:
                            gdf = gdf[gdf["DESA_KEL_1"].str.contains(cari_desa, case=False, na=False)]
                            st.sidebar.success(f"Ditemukan {len(gdf)} data cocok!")
                    elif "DESA" in gdf.columns:
                        cari_desa = st.sidebar.text_input("Cari Nama Desa:")
                        if cari_desa:
                            gdf = gdf[gdf["DESA"].str.contains(cari_desa, case=False, na=False)]
                            st.sidebar.success(f"Ditemukan {len(gdf)} data cocok!")

                    tab1, tab2, tab3 = st.tabs(["🗺️ Peta Interaktif Web", "📊 Peta Statis", "📋 Tabel Data Atribut"])

                    with tab1:
                        st.subheader("Peta Interaktif (Bisa di-Zoom & Diklik)")
                        titik_tengah = [4.1755, 96.8103]
                        m = folium.Map(location=titik_tengah, zoom_start=8, tiles="OpenStreetMap")
                        
                        popup_fields = [pilihan_kolom]
                        if "DESA_KEL_1" in gdf.columns: popup_fields.append("DESA_KEL_1")
                        elif "DESA" in gdf.columns: popup_fields.append("DESA")
                        
                        folium.GeoJson(
                            gdf,
                            name="Data Spasial Aceh",
                            popup=folium.GeoJsonPopup(fields=popup_fields, aliases=[f"Nilai ({pilihan_kolom}):", "Nama Desa:"])
                        ).add_to(m)
                        
                        st_folium(m, width="100%", height=500)

                    with tab2:
                        st.subheader("Peta Poligon Statis")
                        fig, ax = plt.subplots(figsize=(10, 6), clear=True)
                        gdf.plot(
                            column=pilihan_kolom,
                            cmap=pilihan_tema,
                            legend=True,
                            ax=ax,
                            edgecolor="black",
                            linewidth=0.2
                        )
                        ax.grid(True, linestyle="--", alpha=0.3)
                        st.pyplot(fig)

                    with tab3:
                        st.subheader("Tabel Basis Data (Database Attribute)")
                        st.write(f"Menampilkan: {len(gdf)} Baris Data")
                        st.dataframe(gdf.drop(columns="geometry"), height=400)

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat membaca file: {e}")
        else:
            st.error("Pastikan Anda menyertakan file dengan ekstensi `.shp`")
else:
    st.warning("⚠️ Mohon upload file peta secara bersamaan agar aplikasi bisa merender visualisasinya.")
