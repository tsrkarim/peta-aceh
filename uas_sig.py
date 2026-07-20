import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="UAS SIG - TS. Rahmat Karim", layout="wide")
st.title("Aplikasi SIG Visualisasi Fasilitas Desa - Tugas UAS")
st.write("Dibuat oleh: **TS. Rahmat Karim** (NIM: 24146047) - Kelas 01")
st.write("Lokasi Analisis: **Fasilitas Pendidikan & Kesehatan Desa Lampeuneurut, Aceh Besar**")

nama_file_csv = "data/data_uas.csv"

if os.path.exists(nama_file_csv):
    df = pd.read_csv(nama_file_csv)
else:
    st.error("Berkas data_uas.csv tidak ditemukan di folder data!")
    st.stop()

st.sidebar.header("Filter Peta")
kategori_pilihan = st.sidebar.multiselect(
    "Pilih Kategori Objek:",
    options=df['Kategori'].unique(),
    default=df['Kategori'].unique()
)

df_filtered = df[df['Kategori'].isin(kategori_pilihan)]

koordinat_pusat = [5.5150, 95.3130]
peta = folium.Map(location=koordinat_pusat, zoom_start=16, control_scale=True)

for index, row in df_filtered.iterrows():
    # Warna Merah untuk Sekolah/Pondok, Hijau untuk Rumah Sakit/Kesehatan
    warna = 'red' if row['Kategori'] == 'Pendidikan' else 'green'
        
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=f"<b>{row['Nama Tempat']}</b><br>Kategori: {row['Kategori']}",
        tooltip=row['Nama Tempat'],
        icon=folium.Icon(color=warna, icon='info-sign')
    ).add_to(peta)

kolom_peta, kolom_data = st.columns([2, 1])

with kolom_peta:
    st.subheader("Peta Lokasi Fasilitas")
    st_folium(peta, width="100%", height=550)

with kolom_data:
    st.subheader("Tabel Koordinat Objek UAS")
    st.dataframe(df_filtered, use_container_width=True)
    st.write(f"Menampilkan **{len(df_filtered)}** dari total **{len(df)}** objek.")
