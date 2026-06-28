import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import tempfile

st.set_page_config(page_title="Web SIG Aceh Online", layout="wide")

st.title("🗺️ Web SIG Provinsi Aceh (Online via HP)")
st.write("Aplikasi analisis spasial Shapefile menggunakan Streamlit Cloud.")
st.info("💡 **Petunjuk:** Silakan upload 4 file peta sekaligus (.shp, .shx, .dbf, .prj) pada kotak di bawah ini.")

file_diunggah = st.file_uploader(
    "Pilih & Upload file .shp, .shx, .dbf, dan .prj bersamaan:",
    type=["shp", "shx", "dbf", "prj"],
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

                    st.sidebar.header("Pengaturan Peta")
                    pilihan_kolom = st.sidebar.selectbox("Pilih Kolom Data Atribut:", options=kolom_atribut)
                    pilihan_tema = st.sidebar.selectbox("Pilih Tema Warna:", options=["YlOrRd", "viridis", "plasma", "magma", "coolwarm"])

                    fig, ax = plt.subplots(figsize=(10, 6), clear=True)
                    gdf.plot(
                        column=pilihan_kolom,
                        cmap=pilihan_tema,
                        legend=True,
                        legend_kwds={'title': f"Skala: {pilihan_kolom}", 'orientation': "horizontal"},
                        ax=ax,
                        edgecolor="black",
                        linewidth=0.5
                    )
                    ax.set_title(f"Visualisasi Spasial: {pilihan_kolom}", fontsize=14, weight='bold')
                    ax.grid(True, linestyle="--", alpha=0.3)

                    kolom_kiri, kolom_kanan = st.columns([3, 2])
                    with kolom_kiri:
                        st.subheader("Peta Poligon Spasial")
                        st.pyplot(fig)
                    with kolom_kanan:
                        st.subheader("Data Atribut (Tabel)")
                        st.write(f"Total: {len(gdf)} Data")
                        st.dataframe(gdf.drop(columns="geometry"), height=450)

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat membaca file: {e}")
        else:
            st.error("Pastikan Anda menyertakan file dengan ekstensi `.shp`")
else:
    st.warning("⚠️ Belum ada file atau file kurang lengkap. Mohon upload keempat file (.shp, .shx, .dbf, .prj) secara bersamaan agar peta bisa muncul.")
