import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# 1. Pengaturan Halaman Utama
st.set_page_config(page_title="Praktikum SIG Banda Aceh", layout="wide")
st.title("Aplikasi Sistem Informasi Geografis (SIG) Kota Banda Aceh")
st.write("Modul praktikum SIG interaktif menggunakan Python, Streamlit, dan Folium.")

# 2. Penyiapan Data Spasial Wilayah Banda Aceh
nama_file_csv = "data/data_aceh.csv"

if os.path.exists(nama_file_csv):
    df = pd.read_csv(nama_file_csv)
else:
    # Data default sesuai modul praktikum
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

# 3. Fitur Sidebar untuk Filter Kategori
st.sidebar.header("Panel Kontrol & Filter")
kategori_pilihan = st.sidebar.multiselect(
    "Pilih Kategori Objek:",
    options=df['Kategori'].unique(),
    default=df['Kategori'].unique()
)

# Memfilter dataframe
df_filtered = df[df['Kategori'].isin(kategori_pilihan)]

# 4. Membuat Visualisasi Peta Menggunakan Folium
koordinat_pusat = [df['Latitude'].mean(), df['Longitude'].mean()]
peta = folium.Map(location=koordinat_pusat, zoom_start=13, control_scale=True)

# Menambahkan penanda (Marker)
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

# 5. Menampilkan Output pada Grid Streamlit (Dua Kolom)
kolom_peta, kolom_data = st.columns([2, 1])

with kolom_peta:
    st.subheader("Visualisasi Spasial Interaktif")
    st_folium(peta, width="100%", height=500)

with kolom_data:
    st.subheader("Atribut Data (Tabular)")
    st.dataframe(df_filtered, use_container_width=True)
    st.write(f"Menampilkan **{len(df_filtered)}** dari **{len(df)}** total objek di Banda Aceh.")
