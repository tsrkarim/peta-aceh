import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import tempfile

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
                    
                    kolom_atribut = [col for col in gdf.columns if col != "geometry"]

                    # SIDEBAR PENGATURAN
                    st.sidebar.header("⚙️ Pengaturan Peta")
                    pilihan_kolom = st.sidebar.selectbox("Pilih Kolom Data Atribut:", options=kolom_atribut)
                    pilihan_tema = st.sidebar.selectbox("Pilih Tema Warna Peta:", options=["YlOrRd", "viridis", "plasma", "magma", "coolwarm"])
                    
                    st.sidebar.markdown("---")
                    st.sidebar.header("🔍 Fitur Filter Pencarian")
                    
                    # Deteksi kolom nama desa yang tersedia
                    kolom_desa = "DESA_KEL_1" if "DESA_KEL_1" in gdf.columns else ("DESA" if "DESA" in gdf.columns else None)
                    
                    cari_desa = ""
                    if kolom_desa:
                        cari_desa = st.sidebar.text_input("Cari Nama Desa/Kelurahan:")
                    
                    # Proses Filter Data
                    gdf_terfilter = gdf.copy()
                    if cari_desa:
                        gdf_terfilter = gdf[gdf[kolom_desa].str.contains(cari_desa, case=False, na=False)]
                        st.sidebar.success(f"Ditemukan {len(gdf_terfilter)} data cocok!")

                    # MEMBAGIAN MENU MENJADI TAB YANG RAPI & RINGAN
                    tab1, tab2 = st.tabs(["📊 Visualisasi Peta Spasial", "📋 Tabel Atribut & Statistik"])

                    with tab1:
                        st.subheader("Peta Poligon Spasial Provinsi Aceh")
                        fig, ax = plt.subplots(figsize=(10, 6), clear=True)
                        
                        # Gambar peta utama
                        gdf_terfilter.plot(
                            column=pilihan_kolom,
                            cmap=pilihan_tema,
                            legend=True,
                            ax=ax,
                            edgecolor="black",
                            linewidth=0.2
                        )
                        ax.grid(True, linestyle="--", alpha=0.3)
                        ax.set_title(f"Visualisasi Atribut: {pilihan_kolom}", fontsize=12)
                        st.pyplot(fig)

                    with tab2:
                        # FITUR BARU 1: Ringkasan Analisis Statistik Otomatis
                        st.subheader("📊 Analisis Statistik Atribut Pilihan")
                        try:
                            # Jika kolomnya angka, tampilkan statistik deskriptif
                            if gdf_terfilter[pilihan_kolom].dtype in ['int64', 'float64']:
                                col1, col2, col3 = st.columns(3)
                                col1.metric("Nilai Maksimum", f"{gdf_terfilter[pilihan_kolom].max():,}")
                                col2.metric("Nilai Minimum", f"{gdf_terfilter[pilihan_kolom].min():,}")
                                col3.metric("Total Data", f"{len(gdf_terfilter):,}")
                            else:
                                st.write(f"Kolom **{pilihan_kolom}** berisi data teks/kategori.")
                        except:
                            st.write("Gagal memuat analisis statistik untuk kolom ini.")

                        st.markdown("---")
                        
                        # FITUR BARU 2: Tabel Interaktif Berdasarkan Filter Search
                        st.subheader("📋 Basis Data Atribut (Attribute Database Table)")
                        st.write(f"Menampilkan {len(gdf_terfilter)} baris dari total {len(gdf)} data desa.")
                        st.dataframe(gdf_terfilter.drop(columns="geometry"), height=350)

                except Exception as e:
                    st.error(f"Terjadi kesalahan saat membaca file: {e}")
        else:
            st.error("Pastikan Anda menyertakan file dengan ekstensi `.shp`")
else:
    st.warning("⚠️ Mohon upload file peta secara bersamaan agar aplikasi bisa merender visualisasinya.")
