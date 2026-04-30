# Bike Sharing Analysis Project 🚲

Proyek ini adalah analisis data dari Bike Sharing Dataset untuk memenuhi tugas akhir kelas "Belajar Analisis Data dengan Python" di Dicoding.

## Struktur Direktori
- `dashboard/`: Berisi berkas Python untuk dashboard Streamlit dan dataset yang telah dibersihkan.
- `data/`: Dataset asli (day.csv & hour.csv).
- `notebook.ipynb`: Dokumentasi lengkap proses analisis data dari Gathering hingga Explanatory Analysis.
- `requirements.txt`: Daftar library yang digunakan.
- `README.md`: Informasi proyek.
- `url.txt`: Tautan dashboard yang telah dideploy (jika ada).

## Cara Menjalankan Dashboard
1. Pastikan Python terinstal di komputer Anda.
2. Instal semua dependensi yang diperlukan:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run dashboard/dashboard.py
   ```

## Fitur Dashboard
- Filter rentang waktu penyewaan.
- Metrik ringkasan (Total, Rata-rata, Maksimum).
- Visualisasi tren bulanan.
- Analisis pengaruh cuaca dan musim terhadap penyewaan.
- Clustering manual berdasarkan temperatur.
