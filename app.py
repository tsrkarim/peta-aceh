import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import tempfile
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Dashboard SIG Aceh", layout="wide")

# MENU UTAMA DI SIDEBAR
st.sidebar.title("🎮 Navigasi Aplikasi")
menu_pilihan = st.sidebar.selectbox(
    "Pilih Menu Peta:",
    ["📌 Tugas Modul (Banda Aceh)", "🗺️ Unggah Shapefile (Aceh)"]
)

# ==========================================
# MENU 1: TUGAS MODUL BANDA ACEH (CSV/TITIK)
# ==========================================
if menu_pilihan == "📌 Tugas Modul (Banda Aceh)":
    st.title("Aplikasi SIG Kota Banda Aceh (Tugas Modul)")
    st.write("Modul praktikum SIG interaktif menggunakan Python, Streamlit, dan Folium.")
    st.info("💡 Menu ini memuat peta titik landmark Banda Aceh sesuai panduan modul praktikum.")

    nama_file_csv = "data/data_aceh.csv"
    if os.path.exists(nama_file_csv):
        df = pd.read_csv(nama_file_csv)
    else:
        data_lokasi = {
            'Nama Tempat': [
                'Universitas Syiah Kuala (USK)',
                'Masjid Raya Baiturrahman',
                'Museum Tsunami Aceh',
                'RSUD Dr. Zainoel Abidin',
                'Taman Sari (Bustanus Salatin)',
                'PLTD Apung (Situs Sejarah)'
            ],
            'Latitude': [5.5701, 5.5536, 5.5476, 5.5615, 5.5518, 5.5463],
            'Longitude': [95.3695, 95.3172, 95.3153, 95.3426, 95.3175, 95.3056],
            'Kategori': ['Pendidikan', 'Fasilitas Umum', 'Fasilitas Umum', 'Kesehatan', 'Ruang Terbuka', 'Fasilitas Umum']
        }
        df = pd.DataFrame(data_lokasi)

    st.sidebar.header("Filter Kategori")
    kategori_pilihan = st.sidebar.multiselect(
        "Pilih Kategori Objek:",
        options=df['Kategori'].unique(),
        default=df['Kategori'].unique()
    )

    df_filtered = df[df['Kategori'].isin(kategori_pilihan)]

    koordinat_pusat = [df['Latitude'].mean(), df['Longitude'].mean()]
    peta = folium.Map(location=koordinat_pusat, zoom_start=13, control_scale=True)

    for index, row in df_filtered.iterrows():
        warna = 'blue'
        if row['Kategori'] == 'Pendidikan':
            warna = 'red'
        elif row['Kategori'] == 'Kesehatan':
            warna = 'green'
        elif row['Kategori'] == 'Ruang Terbuka':
            warna = 'orange'
        elif row['Kategori'] == 'Kuliner':
            warna = 'purple'
        elif row['Kategori'] == 'Tempat Tinggal':
            warna = 'cadetblue'
            
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=f"<b>{row['Nama Tempat']}</b><br>Kategori: {row['Kategori']}",
            tooltip=row['Nama Tempat'],
            icon=folium.Icon(color=warna, icon='info-sign')
        ).add_to(peta)

    kolom_peta, kolom_data = st.columns([2, 1])
    with kolom_peta:
        st.subheader("Visualisasi Spasial Interaktif")
        st_folium(peta, width="100%", height=500)
    with kolom_data:
        st.subheader("Atribut Data (Tabular)")
        st.dataframe(df_filtered, use_container_width=True)
        st.write(f"Menampilkan **{len(df_filtered)}** dari **{len(df)}** total objek.")

# ==========================================
# MENU 2: UNGGAH SHAPEFILE (POLIGON ACEH)
# ==========================================
elif menu_pilihan == "🗺️ Unggah Shapefile (Aceh)":
    st.title("Web SIG Provinsi Aceh - Unggah Shapefile")
    st.write("Aplikasi analisis spasial berkas Shapefile menggunakan Streamlit Cloud.")
    st.info("💡 **Petunjuk:** Silakan unggah file peta (.shp, .shx, .dbf, .prj) secara bersamaan pada kotak di bawah ini.")

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
                        kolom_atribut = [col for col in gdf.columns if col != "geometry"]

                        st.sidebar.header("⚙️ Pengaturan Peta")
                        pilihan_kolom = st.sidebar.selectbox("Pilih Kolom Data Atribut:", options=kolom_atribut)
                        pilihan_tema = st.sidebar.selectbox("Pilih Tema Warna Peta:", options=["YlOrRd", "viridis", "plasma", "magma", "coolwarm"])

                        tab1, tab2 = st.tabs(["📊 Visualisasi Peta Spasial", "📋 Tabel Atribut"])

                        with tab1:
                            st.subheader("Peta Poligon Spasial Provinsi Aceh")
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

                        with tab2:
                            st.subheader("📋 Basis Data Atribut")
                            st.write(f"Total Data: {len(gdf)} baris.")
                            st.dataframe(gdf.drop(columns="geometry"), height=350)

                    except Exception as e:
                        st.error(f"Terjadi kesalahan saat membaca file: {e}")
            else:
                st.error("Pastikan Anda menyertakan file dengan ekstensi `.shp`")
    else:
        st.warning("⚠️ Mohon upload file peta secara bersamaan untuk merender visualisasinya.")
