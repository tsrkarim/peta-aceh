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
                    st.sidebar.header("🔍 Fitur Pencarian Dinamis")
                    
                    # Cek kolom nama desa yang tersedia
                    kolom_desa = "DESA_KEL_1" if "DESA_KEL_1" in gdf.columns else ("DESA" if "DESA" in gdf.columns else None)
                    
                    cari_desa = ""
                    if kolom_desa:
                        cari_desa = st.sidebar.text_input("Ketik Nama Desa untuk Peta Interaktif:")
                    
                    # Filter data jika ada pencarian
                    gdf_terfilter = gdf.copy()
                    if cari_desa:
                        gdf_terfilter = gdf[gdf[kolom_desa].str.contains(cari_desa, case=False, na=False)]
                        st.sidebar.success(f"Ditemukan {len(gdf_terfilter)} data cocok!")

                    tab1, tab2, tab3 = st.tabs(["🗺️ Peta Interaktif Web", "📊 Peta Statis Global", "📋 Tabel Data Atribut"])

                    with tab1:
                        st.subheader("Peta Interaktif (Mode Cepat)")
                        m = folium.Map(location=[4.1755, 96.8103], zoom_start=8, tiles="OpenStreetMap")
                        
                        if cari_desa and not gdf_terfilter.empty:
                            popup_fields = [pilihan_kolom, kolom_desa]
                            folium.GeoJson(
                                gdf_terfilter,
                                name="Hasil Pencarian Desa",
                                popup=folium.GeoJsonPopup(fields=popup_fields, aliases=[f"Nilai ({pilihan_kolom}):", "Nama Desa:"])
                            ).add_to(m)
                            st.caption(f"Menampilkan hasil pencarian untuk desa: **{cari_desa}**")
                        else:
                            st.warning("💡 **Tips Ujian:** Peta interaktif sengaja dikosongkan agar loading instan. Silakan ketik nama desa pada menu **Fitur Pencarian Dinamis** di sebelah kiri untuk memunculkan wilayah desanya secara interaktif!")
                        
                        st_folium(m, width="100%", height=450)

                    with tab2:
                        st.subheader("Peta Poligon Statis Keseluruhan Wilayah")
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
                        st.write(f"Total Database: {len(gdf_terfilter)} Baris Data")
                        st.dataframe(gdf_terfilter.drop(columns="geometry"), height=400)

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat membaca file: {e}")
        else:
            st.error("Pastikan Anda menyertakan file dengan ekstensi `.shp`")
else:
    st.warning("⚠️ Mohon upload file peta secara bersamaan agar aplikasi bisa merender visualisasinya.")
