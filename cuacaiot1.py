import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import json

# 🔹 Konfigurasi kredensial Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(credentials_info)

# Autentikasi ke Google Sheets
client = gspread.authorize(creds)

# 🔹 ID dan Nama Sheet
SHEET_ID = "1oChB07rsg1_RZcvfwkoEFGd58jc00HX3wz01tYoDKog"
SHEET_NAME = "SensorData"

# 🔹 Fungsi untuk membaca data dari Google Sheets
@st.cache_data(ttl=600)
def get_data():
    try:
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        data = sheet.get_all_records()
        df = pd.DataFrame(data)
        
        # 🔹 Normalisasi nama kolom agar tidak ada spasi
        df.columns = df.columns.str.strip().str.lower()
        
        # 🔹 Pastikan kolom "timestamp" ada dalam data
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
            df.set_index("timestamp", inplace=True)
        else:
            st.error("Kolom 'timestamp' tidak ditemukan dalam data!")
            return pd.DataFrame()
        
        return df
    except Exception as e:
        st.error(f"Terjadi kesalahan saat mengambil data: {e}")
        return pd.DataFrame()

# 🔹 Streamlit UI
st.set_page_config(page_title="Dashboard Cuaca", layout="wide")

st.title("🌤 Dashboard Monitoring Cuaca")
st.write("📡 Data diperbarui langsung dari Google Sheets")

# 🔹 Load data
df = get_data()

# 🔹 Cek apakah data tersedia
if df.empty:
    st.warning("Data tidak tersedia. Pastikan Google Sheets memiliki data terbaru.")
else:
    # 🔹 Pilih rentang waktu
    min_date, max_date = df.index.min(), df.index.max()
    date_range = st.slider("Pilih Rentang Waktu:", min_value=min_date, max_value=max_date, value=(min_date, max_date))
    df_filtered = df.loc[date_range[0]:date_range[1]]
    
    # 🔹 Tampilkan tabel data
    st.subheader("📋 Data Cuaca Terbaru")
    st.dataframe(df_filtered.tail(10))

    # 🔹 Visualisasi Grafik dengan Plotly
    st.subheader("📈 Grafik Data Cuaca")

    # Grafik Kelembaban
    fig_humidity = px.line(df_filtered, x=df_filtered.index, y="kelembaban", title="Grafik Kelembaban (%)",
                           labels={"kelembaban": "Kelembaban (%)", "timestamp": "Waktu"},
                           line_shape="spline", markers=True, color_discrete_sequence=["#00BFFF"])
    
    # Grafik Kecepatan Angin
    fig_wind = px.line(df_filtered, x=df_filtered.index, y="kecepatan angin", title="Grafik Kecepatan Angin (km/h)",
                       labels={"kecepatan angin": "Kecepatan Angin (km/h)", "timestamp": "Waktu"},
                       line_shape="spline", markers=True, color_discrete_sequence=["#FF4500"])

    # 🔹 Tampilkan Grafik
    st.plotly_chart(fig_humidity, use_container_width=True)
    st.plotly_chart(fig_wind, use_container_width=True)

    # 🔹 Distribusi Klasifikasi Cuaca
    st.subheader("🌦️ Distribusi Klasifikasi Cuaca")
    fig_weather = px.bar(df_filtered["cuaca (decision tree)"].value_counts(), 
                         title="Frekuensi Prediksi Cuaca (Decision Tree)",
                         labels={"index": "Klasifikasi Cuaca", "value": "Jumlah"},
                         color=df_filtered["cuaca (decision tree)"].value_counts().index,
                         color_discrete_sequence=px.colors.qualitative.Set3)

    st.plotly_chart(fig_weather, use_container_width=True)

    # 🔹 Prediksi Cuaca Terbaru
    st.subheader("📝 Prediksi Cuaca Terbaru")
    latest_weather_dt = df_filtered.iloc[-1]["cuaca (decision tree)"]
    latest_weather_nb = df_filtered.iloc[-1]["cuaca (naive bayes)"]

    st.write(f"🌤 **Prediksi Decision Tree:** {latest_weather_dt}")
    st.write(f"🌧 **Prediksi Naive Bayes:** {latest_weather_nb}")
