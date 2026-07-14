import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tempfile

st.set_page_config(page_title="Web SIG Aceh Online", layout="wide")

st.title("🗺️ Web SIG Provinsi Aceh (Analisis Shapefile)")
st.write("Aplikasi analisis spasial Shapefile menggunakan Streamlit Cloud.")

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
                    
                    st.sidebar.markdown("---")
                    st.sidebar.header("🔍 Fitur Filter Pencarian")
                    kolom_desa = "DESA_KEL_1" if "DESA_KEL_1" in gdf.columns else ("DESA" if "DESA" in gdf.columns else None)
                    
                    cari_desa = ""
                    if kolom_desa:
                        cari_desa = st.sidebar.text_input("Cari Nama Desa/Kelurahan:")
                    
                    gdf_terfilter = gdf.copy()
                    if cari_desa:
                        gdf_terfilter = gdf[gdf[kolom_desa].str.contains(cari_desa, case=False, na=False)]
                        st.sidebar.success(f"Ditemukan {len(gdf_terfilter)} data cocok!")

                    tab1, tab2, tab3 = st.tabs(["🗺️ Peta Visualisasi Spasial", "📊 Grafik Analisis Data", "📋 Tabel Atribut & Statistik"])

                    with tab1:
                        st.subheader("Peta Poligon Spasial Provinsi Aceh")
                        fig, ax = plt.subplots(figsize=(10, 6), clear=True)
                        gdf_terfilter.plot(
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
                        st.subheader("📊 Grafik 10 Wilayah dengan Nilai Tertinggi")
                        try:
                            if gdf_terfilter[pilihan_kolom].dtype in ['int64', 'float64']:
                                data_grafik = gdf_terfilter.nlargest(10, pilihan_kolom)
                                fig_bar, ax_bar = plt.subplots(figsize=(10, 5))
                                label_x = kolom_desa if kolom_desa else pilihan_kolom
                                sns.barplot(
                                    x=data_grafik[pilihan_kolom], 
                                    y=data_grafik[label_x].astype(str), 
                                    palette="Blues_r", 
                                    ax=ax_bar
                                )
                                ax_bar.set_title(f"Top 10 Wilayah Berdasarkan {pilihan_kolom}")
                                plt.tight_layout()
                                st.pyplot(fig_bar)
                            else:
                                st.warning(f"⚠️ Kolom '{pilihan_kolom}' berisi data teks. Pilih kolom angka untuk memunculkan grafik.")
                        except Exception as err:
                            st.error(f"Gagal memuat grafik: {err}")

                    with tab3:
                        st.subheader("📋 Basis Data Atribut")
                        st.dataframe(gdf_terfilter.drop(columns="geometry"), height=350)

                except Exception as e:
                    st.error(f"Terjadi kesalahan: {e}")
        else:
            st.error("File .shp tidak ditemukan.")
else:
    st.warning("⚠️ Silakan upload file peta (.shp, .shx, .dbf, .prj) bersamaan.")
