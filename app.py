# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from influxdb_client import InfluxDBClient
import os

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(page_title="Dashboard Planta Productiva", layout="wide")

# --- Estilo visual ---
st.markdown("""
    <style>
        body {
            background-color: #FFFFFF;
            color: #1B4332;
        }
        .stApp {
            background-color: #FFFFFF;
        }
        .card {
            background-color: #F6FFF8;
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #95D5B2;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }
        h2, h3 {
            color: #2D6A4F;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------
# CONFIGURACIÓN DE INFLUXDB
# -----------------------------
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "https://us-east-1-1.aws.cloud2.influxdata.com")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "TU_TOKEN_AQUI")  # ⚠️ mejor usar secrets en producción
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "0925ccf91ab36478")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "EXTREME_MANUFACTURING")

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
query_api = client.query_api()

# -----------------------------
# CONTROLES SUPERIORES
# -----------------------------
st.title("🌿 Dashboard — Monitoreo Planta Productiva")
st.write("Visualización en tiempo real de sensores **DHT22** y **MPU6050** desde InfluxDB.")

rango = st.slider(
    "Selecciona el rango de tiempo (días hacia atrás):",
    min_value=1, max_value=30, value=3
)

# -----------------------------
# CONSULTA DE DATOS
# -----------------------------
def consultar_datos(sensor, rango):
    if sensor == "DHT22":
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -{rango}d)
            |> filter(fn: (r) => r._measurement == "studio-dht22")
            |> filter(fn: (r) => r._field == "humedad" or r._field == "temperatura" or r._field == "sensacion_termica")
        '''
    else:
        query = f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -{rango}d)
            |> filter(fn: (r) => r._measurement == "mpu6050")
            |> filter(fn: (r) =>
                r._field == "accel_x" or r._field == "accel_y" or r._field == "accel_z" or
                r._field == "gyro_x" or r._field == "gyro_y" or r._field == "gyro_z" or
                r._field == "temperature")
        '''
    try:
        df = query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
        if isinstance(df, list):
            df = pd.concat(df)
        if df.empty:
            return pd.DataFrame()
        df = df[["_time", "_field", "_value"]]
        df.columns = ["Tiempo", "Variable", "Valor"]
        df["Tiempo"] = pd.to_datetime(df["Tiempo"])
        return df
    except Exception as e:
        st.error(f"Error al consultar {sensor}: {e}")
        return pd.DataFrame()

df_dht = consultar_datos("DHT22", rango)
df_mpu = consultar_datos("MPU6050", rango)

# -----------------------------
# DISEÑO EN DOS COLUMNAS
# -----------------------------
col1, col2 = st.columns(2)

# --- Columna Izquierda: DHT22 ---
with col1:
    st.markdown("## 🌡️ Sensor DHT22")
    if df_dht.empty:
        st.warning("No hay datos recientes de DHT22.")
    else:
        for var in df_dht["Variable"].unique():
            sub_df = df_dht[df_dht["Variable"] == var]
            with st.container():
                st.markdown(f"<div class='card'><h3>{var}</h3>", unsafe_allow_html=True)
                fig = px.line(
                    sub_df,
                    x="Tiempo",
                    y="Valor",
                    title="",
                    template="plotly_white",
                    color_discrete_sequence=["#2D6A4F"]
                )
                fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

# --- Columna Derecha: MPU6050 ---
with col2:
    st.markdown("## ⚙️ Sensor MPU6050")
    if df_mpu.empty:
        st.warning("No hay datos recientes de MPU6050.")
    else:
        for var in df_mpu["Variable"].unique():
            sub_df = df_mpu[df_mpu["Variable"] == var]
            with st.container():
                st.markdown(f"<div class='card'><h3>{var}</h3>", unsafe_allow_html=True)
                fig = px.line(
                    sub_df,
                    x="Tiempo",
                    y="Valor",
                    title="",
                    template="plotly_white",
                    color_discrete_sequence=["#40916C"]
                )
                fig.update_layout(margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# TABLA RESUMEN FINAL
# -----------------------------
st.markdown("---")
st.markdown("### 📋 Resumen Estadístico General")

if not df_dht.empty or not df_mpu.empty:
    resumen = pd.concat([df_dht.assign(Sensor="DHT22"), df_mpu.assign(Sensor="MPU6050")])
    st.dataframe(resumen.groupby(["Sensor", "Variable"])["Valor"].describe()[["mean", "std", "min", "max"]])
else:
    st.info("Sin datos para mostrar estadísticas.")
