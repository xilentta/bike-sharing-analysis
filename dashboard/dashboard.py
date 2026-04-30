import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Membaca data harian dari folder data/
    df = pd.read_csv("data/day.csv")
    df['dteday'] = pd.to_datetime(df['dteday'])
    
    # Menambahkan label untuk cuaca jika belum ada
    if 'weather_label' not in df.columns:
        weather_map = {1: 'Clear', 2: 'Misty', 3: 'Light Snow/Rain', 4: 'Heavy Rain'}
        df['weather_label'] = df['weathersit'].map(weather_map)
        
    # Menambahkan label untuk musim jika belum ada
    if 'season_label' not in df.columns:
        season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
        df['season_label'] = df['season'].map(season_map)
        
    return df

main_df = load_data()

# Tambahkan kolom demand_cluster jika belum ada
def classify_day(row):
    if row['cnt'] >= 6000:
        return 'High Demand'
    elif row['cnt'] >= 4000:
        return 'Medium Demand'
    else:
        return 'Low Demand'

if 'demand_cluster' not in main_df.columns:
    main_df['demand_cluster'] = main_df.apply(classify_day, axis=1)

# ── Sidebar ──────────────────────────────────────────────────────────────────
min_date = main_df["dteday"].min()
max_date = main_df["dteday"].max()

with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 10px 0 20px 0;'>
            <div style='font-size: 64px;'>🚲</div>
            <div style='font-size: 18px; font-weight: bold; color: #3970F1;'>Bike Sharing</div>
            <div style='font-size: 12px; color: gray;'>Washington D.C. 2011-2012</div>
        </div>
    """, unsafe_allow_html=True)

    date_input = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    if isinstance(date_input, (list, tuple)) and len(date_input) == 2:
        start_date, end_date = date_input
    else:
        st.info("Silakan pilih tanggal akhir terlebih dahulu.")
        st.stop()

filtered_df = main_df[
    (main_df["dteday"] >= pd.Timestamp(start_date)) &
    (main_df["dteday"] <= pd.Timestamp(end_date))
]

# ── Header & Metrics ─────────────────────────────────────────────────────────
st.header('Bike Sharing Dashboard ')

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Penyewaan", value=f"{filtered_df['cnt'].sum():,}")
with col2:
    st.metric("Rata-rata Harian", value=f"{round(filtered_df['cnt'].mean()):,}")
with col3:
    st.metric("Penyewaan Tertinggi", value=f"{filtered_df['cnt'].max():,}")

# ── Pertanyaan 1: Tren Bulanan ───────────────────────────────────────────────
st.subheader('Pertanyaan 1: Tren Penyewaan Bulanan')

if len(filtered_df) < 2:
    st.warning("Rentang waktu terlalu pendek.")
else:
    try:
        monthly_df = filtered_df.resample('ME', on='dteday').agg({'cnt': 'sum'})
    except ValueError:
        monthly_df = filtered_df.resample('M', on='dteday').agg({'cnt': 'sum'})

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(monthly_df.index, monthly_df['cnt'], marker='o', linewidth=2, color='#3970F1')
    ax.fill_between(monthly_df.index, monthly_df['cnt'], alpha=0.1, color='#3970F1')
    ax.set_title('Total Penyewaan Sepeda per Bulan', fontsize=16)
    ax.set_xlabel('Bulan')
    ax.set_ylabel('Jumlah Penyewaan')
    ax.grid(True, linestyle='--', alpha=0.5)
    for x, y in zip(monthly_df.index, monthly_df['cnt']):
        ax.annotate(f'{y:,}', (x, y), textcoords="offset points",
                    xytext=(0, 8), ha='center', fontsize=7)
    st.pyplot(fig)
    st.caption("**Insight:** Penyewaan tumbuh konsisten dari 2011 ke 2012. Puncak tertinggi September 2012 (~218K).")

# ── Pertanyaan 2: Pola per Jam ───────────────────────────────────────────────
st.subheader('Pertanyaan 2: Jam Paling Ramai dan Paling Sepi')

try:
    # Membaca data per jam dari folder data/
    hour_df = pd.read_csv("data/hour.csv")
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    hourly_filtered = hour_df[
        (hour_df["dteday"] >= pd.Timestamp(start_date)) &
        (hour_df["dteday"] <= pd.Timestamp(end_date))
    ]
    hourly_rentals = hourly_filtered.groupby('hr')['cnt'].mean()
    
    colors = ['#E74C3C' if h in [8, 17, 18] else '#3498DB' for h in hourly_rentals.index]
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(hourly_rentals.index, hourly_rentals.values, color=colors, edgecolor='white')
    ax.set_title('Rata-rata Penyewaan per Jam dalam Sehari', fontsize=16)
    ax.set_xlabel('Jam (0-23)')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_xticks(range(0, 24))
    
    # Anotasi angka di atas balok telah dihapus agar visualisasi lebih bersih
    
    st.pyplot(fig)
    st.caption("**Insight:** Dua puncak utama: pukul 08:00 (berangkat kerja) dan 17:00-18:00 (pulang kerja).")
    
except Exception as e:
    st.error(f"Gagal memuat data per jam: {e}")
    st.info("Pastikan file `hour.csv` tersedia di folder `data/`.")

# ── Pertanyaan 3: Cuaca & Musim ──────────────────────────────────────────────
st.subheader('Pertanyaan 3: Pengaruh Cuaca dan Musim')

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

weather_order = filtered_df.groupby('weather_label')['cnt'].mean().sort_values(ascending=False).index
sns.barplot(x='weather_label', y='cnt', data=filtered_df,
            order=weather_order, palette='Blues_d', ax=axes[0])
axes[0].set_title('Rata-rata Penyewaan per Kondisi Cuaca', fontsize=13)
axes[0].set_xlabel('Kondisi Cuaca')
axes[0].set_ylabel('Rata-rata Penyewaan')

# Anotasi angka di atas balok telah dihapus agar visualisasi lebih bersih

season_order = filtered_df.groupby('season_label')['cnt'].mean().sort_values(ascending=False).index
sns.barplot(x='season_label', y='cnt', data=filtered_df,
            order=season_order, palette='Oranges_d', ax=axes[1])
axes[1].set_title('Rata-rata Penyewaan per Musim', fontsize=13)
axes[1].set_xlabel('Musim')
axes[1].set_ylabel('Rata-rata Penyewaan')

# Anotasi angka di atas balok telah dihapus agar visualisasi lebih bersih

st.pyplot(fig)
st.caption("**Insight:** Cuaca cerah & musim gugur menghasilkan penyewaan tertinggi. Hujan menurunkan penyewaan drastis.")

# ── Analisis Lanjutan: Manual Clustering ─────────────────────────────────────
st.subheader('Analisis Lanjutan: Manual Clustering Demand Level')

cluster_order = ['Low Demand', 'Medium Demand', 'High Demand']
palette = {'Low Demand': '#E74C3C', 'Medium Demand': '#F39C12', 'High Demand': '#27AE60'}

existing_clusters = [c for c in cluster_order if c in filtered_df['demand_cluster'].unique()]

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(x='demand_cluster', y='cnt', data=filtered_df,
                order=existing_clusters, palette=palette, ax=ax)
    ax.set_title('Distribusi Penyewaan per Cluster', fontsize=13)
    ax.set_xlabel('Cluster')
    ax.set_ylabel('Total Penyewaan')
    st.pyplot(fig)

with col2:
    cluster_summary = filtered_df.groupby('demand_cluster').agg(
        Jumlah_Hari=('cnt', 'count'),
        Rata_rata=('cnt', 'mean'),
    ).round(0).loc[existing_clusters]
    cluster_summary['Rata_rata'] = cluster_summary['Rata_rata'].astype(int)
    st.markdown("**Ringkasan Cluster:**")
    st.dataframe(cluster_summary, use_container_width=True)
    st.markdown("""
    - 🟢 **High Demand**: Hari cuaca cerah, musim gugur/panas
    - 🟡 **Medium Demand**: Kondisi campuran, penggunaan normal
    - 🔴 **Low Demand**: Musim semi, hujan, atau awal layanan 2011
    """)

