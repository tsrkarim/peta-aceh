import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os

# 1. Konfigurasi Halaman Web
st.set_page_config(page_title="Web SIG Lanjutan2 Offline", layout="wide")

st.title("🗺️ Web SIG Lanjutan2: Membaca Data Capil Aceh (Offline)")
st.write("Modul mengajar: Membaca file Shapefile (.shp) Capil Aceh secara lokal.")

# 2. JALUR FILE KHUSUS HP (Sudah diperbaiki)
PATH_DATA = os.path.join("/sdcard", "geospatial", "data", "DUKCAPIL_ACEH.shp")

# 3. Memeriksa apakah file data benar ada di folder
if not os.path.exists(PATH_DATA):
    st.error(
        f"❌ File tidak ditemukan di: `{PATH_DATA}`. "
        "Pastikan folder `geospatial` dan folder `data` di dalamnya sudah dibuat di memori internal HP, "
        "serta file `.shp`, `.shx`, `.dbf`, dan `.prj` sudah ditaruh di sana."
    )
else:

    # 4. Membaca Data Menggunakan Geopandas dengan Cache
    @st.cache_data
    def muat_data_spasial(path):
        data = gpd.read_file(path)

        # Menghapus kolom 'geometry' hanya untuk keperluan list dropdown sidebar
        daftar_kolom = [col for col in data.columns if col != "geometry"]

        return data, daftar_kolom

    with st.spinner("Sedang membaca data spasial lokal..."):
        gdf, kolom_atribut = muat_data_spasial(PATH_DATA)

    # 5. Kontrol Interaktif Sidebar
    st.sidebar.header("Pengaturan Peta")

    pilihan_kolom = st.sidebar.selectbox(
        "Pilih Kolom Data Atribut untuk Pewarnaan:",
        options=kolom_atribut
    )

    pilihan_tema = st.sidebar.selectbox(
        "Pilih Tema Warna (Colormap):",
        options=["YlOrRd", "viridis", "plasma", "magma", "coolwarm"]
    )

    # 6. Membuat Visualisasi Peta Menggunakan Matplotlib
    fig, ax = plt.subplots(figsize=(10, 6), clear=True)

    try:
        # Menggambar peta choropleth
        gdf.plot(
            column=pilihan_kolom,
            cmap=pilihan_tema,
            legend=True,
            legend_kwds={
                'label': f"Skala: {pilihan_kolom}",
                'orientation': "horizontal"
            },
            ax=ax,
            edgecolor="black",
            linewidth=0.5
        )

        ax.set_title(
            f"Visualisasi Spasial Provinsi: {pilihan_kolom}",
            fontsize=14,
            weight='bold'
        )

        ax.set_xlabel("Bujur (Longitude)")
        ax.set_ylabel("Lintang (Latitude)")
        ax.grid(True, linestyle="--", alpha=0.3)

        # Layout Tampilan Streamlit
        kolom_kiri, kolom_kanan = st.columns([3, 2])

        with kolom_kiri:
            st.subheader("Peta Poligon Spasial")
            st.pyplot(fig)

        with kolom_kanan:
            st.subheader("Data Atribut (Tabel)")
            st.write(f"Total: {len(gdf)} Data")

            # Tampilkan tabel tanpa kolom geometri agar ringan
            st.dataframe(
                gdf.drop(columns="geometry"),
                height=450
            )

    except Exception as e:
        st.warning(
            "Gagal mewarnai berdasarkan kolom tersebut. Menampilkan peta dasar..."
        )

        gdf.plot(
            ax=ax,
            facecolor="lightblue",
            edgecolor="black",
            linewidth=0.5
        )

        st.pyplot(fig)
