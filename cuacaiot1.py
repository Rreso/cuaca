import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import json

# 🔹 Konfigurasi kredensial Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials_info = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = Credentials.from_service_account_info(credentials_info, scopes=scope)

# Autentikasi ke Google Sheets
client = gspread.authorize(creds)

# 🔹 ID dan Nama Sheet
SHEET_ID = "1oChB07rsg1_RZcvfwkoEFGd58jc00HX3wz01tYoDKog"
SHEET_NAME = "SensorData"

# 🔹 Fungsi untuk membaca data dari Google Sheets
def get_data():
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

    return df

# 🔹 Streamlit UI
st.set_page_config(page_title="Monitoring Cuaca Polibatam", layout="wide")

st.title("🌤 Monitoring Cuaca Politeknik Negeri Batam")
st.write("📡 Data diperbarui langsung dari Sistem Monitoring")

# 🔹 Load data
df = get_data()

# 🔹 Cek apakah data tersedia
if df.empty:
    st.warning("Data tidak tersedia. Pastikan Google Sheets memiliki data terbaru.")
else:
    # 🔹 Tampilkan tabel data
    st.subheader("📋 Data Cuaca Terbaru")
    st.dataframe(df.tail(10))

    # 🔹 Prediksi Cuaca Terbaru
    st.subheader("📝 Prediksi Cuaca Realtime")
    latest_weather_dt = df.iloc[-1]["cuaca (decision tree)"]
    latest_weather_nb = df.iloc[-1]["cuaca (naive bayes)"]

    st.markdown(f"<h3> Decision Tree: {latest_weather_dt}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h3> Naive Bayes: {latest_weather_nb}</h2>", unsafe_allow_html=True)

    # 🔹 Visualisasi Grafik dengan Plotly
    st.subheader("📈 Grafik Data Cuaca")

    # Grafik Kelembaban
    fig_humidity = px.line(df, x=df.index, y="suhu", title="Grafik Suhu (%)",
                           labels={"suhu": "Suhu (°C)", "timestamp": "Waktu"},
                           line_shape="spline", markers=True, color_discrete_sequence=["#FF7F00"])
    
    # Grafik Kelembaban
    fig_humidity = px.line(df, x=df.index, y="kelembaban", title="Grafik Kelembaban (%)",
                           labels={"kelembaban": "Kelembaban (%)", "timestamp": "Waktu"},
                           line_shape="spline", markers=True, color_discrete_sequence=["#00BFFF"])
    
    # Grafik Kecepatan Angin
    fig_wind = px.line(df, x=df.index, y="kecepatan angin", title="Grafik Kecepatan Angin (km/h)",
                       labels={"kecepatan angin": "Kecepatan Angin (km/h)", "timestamp": "Waktu"},
                       line_shape="spline", markers=True, color_discrete_sequence=["#FF4500"])

    # 🔹 Tampilkan Grafik
    st.plotly_chart(fig_temperature, use_container_width=True)
    st.plotly_chart(fig_humidity, use_container_width=True)
    st.plotly_chart(fig_wind, use_container_width=True)



