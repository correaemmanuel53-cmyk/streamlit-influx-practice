import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Cargar variables de entorno ---
load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

# --- Configuración de la página ---
st.set_page_config(page_title="📊 Tablero de Digitalización de Planta", layout="wide")

# --- Estilos personalizados ---
st.markdown("""
    <style>
        body {
            color: black;
            background-color: white;
        }
        .main {
            background-color: white;
            color: black;
        }
        h1, h2, h3, h4 {
            color: black !important;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stPlotlyChart {
            border: 1px solid #0A7B36;
            border-radius: 15px;
            padding: 15px;
            background-color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- Título principal ---
st.title("📊 Tablero de Digitalización de Planta")
st.write("Visualización de datos en tiempo real desde InfluxDB.")

# --- Conexión a InfluxDB ---
try:
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = client.query_api()
except Exception as e:
    st.error(f"Error de conexión con InfluxDB: {e}")
    st.stop()

# --- Filtros ---
rango = st.slider("Selecciona el rango de tiempo (días hacia atrás):", min_value=1, max_value=30, value=3)

# --- Consultas por sensor ---
consultas = {
    "DHT22": f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -{rango}d)
            |> filter(fn: (r) => r._measurement == "studio-dht22")
            |> filter(fn: (r) => r._field == "humedad" or r._field == "temperatura" or r._field == "sensacion_termica")
    ''',
    "MPU6050": f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -{rango}d)
            |> filter(fn: (r) => r._measurement == "mpu6050")
            |> filter(fn: (r) =>
                r._field == "accel_x" or r._field == "accel_y" or r._field == "accel_z" or
                r._field == "gyro_x" or r._field == "gyro_y" or r._field == "gyro_z" or
                r._field == "temperature")
    '''
}

# --- Layout en dos columnas ---
col1, col2 = st.columns(2)

def mostrar_sensor(nombre, query, columna):
    with columna:
        st.subheader(f"📟 Sensor {nombre}")
        try:
            df = query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
            if isinstance(df, list):
                df = pd.concat(df)
        except Exception as e:
            st.error(f"Error al consultar {nombre}: {e}")
            return

        if df.empty:
            st.warning(f"⚠️ No hay datos disponibles para {nombre}.")
            return

        # Limpiar datos
        df = df[["_time", "_field", "_value"]]
        df = df.rename(columns={"_time": "Tiempo", "_field": "Variable", "_value": "Valor"})
        df["Tiempo"] = pd.to_datetime(df["Tiempo"])

        # Graficar cada variable
        for var in df["Variable"].unique():
            sub_df = df[df["Variable"] == var]
            fig = px.line(
                sub_df,
                x="Tiempo",
                y="Valor",
                title=f"{var}",
                template="plotly_white",
                color_discrete_sequence=["#0A7B36"]
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                title_font=dict(color="black"),
                font=dict(color="black")
            )
            st.plotly_chart(fig, use_container_width=True)

        # Estadísticas
        with st.expander("📋 Estadísticas descriptivas"):
            st.dataframe(df.describe())

# Mostrar ambos sensores
mostrar_sensor("DHT22", consultas["DHT22"], col1)
mostrar_sensor("MPU6050", consultas["MPU6050"], col2)
import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Cargar variables de entorno ---
load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

# --- Configuración de la página ---
st.set_page_config(page_title="📊 Tablero de Digitalización de Planta", layout="wide")

# --- Estilos personalizados ---
st.markdown("""
    <style>
        body {
            color: black;
            background-color: white;
        }
        .main {
            background-color: white;
            color: black;
        }
        h1, h2, h3, h4 {
            color: black !important;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stPlotlyChart {
            border: 1px solid #0A7B36;
            border-radius: 15px;
            padding: 15px;
            background-color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- Título principal ---
st.title("📊 Tablero de Digitalización de Planta")
st.write("Visualización de datos en tiempo real desde InfluxDB.")

# --- Conexión a InfluxDB ---
try:
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = client.query_api()
except Exception as e:
    st.error(f"Error de conexión con InfluxDB: {e}")
    st.stop()

# --- Filtros ---
rango = st.slider("Selecciona el rango de tiempo (días hacia atrás):", min_value=1, max_value=30, value=3)

# --- Consultas por sensor ---
consultas = {
    "DHT22": f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -{rango}d)
            |> filter(fn: (r) => r._measurement == "studio-dht22")
            |> filter(fn: (r) => r._field == "humedad" or r._field == "temperatura" or r._field == "sensacion_termica")
    ''',
    "MPU6050": f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -{rango}d)
            |> filter(fn: (r) => r._measurement == "mpu6050")
            |> filter(fn: (r) =>
                r._field == "accel_x" or r._field == "accel_y" or r._field == "accel_z" or
                r._field == "gyro_x" or r._field == "gyro_y" or r._field == "gyro_z" or
                r._field == "temperature")
    '''
}

# --- Layout en dos columnas ---
col1, col2 = st.columns(2)

def mostrar_sensor(nombre, query, columna):
    with columna:
        st.subheader(f"📟 Sensor {nombre}")
        try:
            df = query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
            if isinstance(df, list):
                df = pd.concat(df)
        except Exception as e:
            st.error(f"Error al consultar {nombre}: {e}")
            return

        if df.empty:
            st.warning(f"⚠️ No hay datos disponibles para {nombre}.")
            return

        # Limpiar datos
        df = df[["_time", "_field", "_value"]]
        df = df.rename(columns={"_time": "Tiempo", "_field": "Variable", "_value": "Valor"})
        df["Tiempo"] = pd.to_datetime(df["Tiempo"])

        # Graficar cada variable
        for var in df["Variable"].unique():
            sub_df = df[df["Variable"] == var]
            fig = px.line(
                sub_df,
                x="Tiempo",
                y="Valor",
                title=f"{var}",
                template="plotly_white",
                color_discrete_sequence=["#0A7B36"]
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                title_font=dict(color="black"),
                font=dict(color="black")
            )
            st.plotly_chart(fig, use_container_width=True)

        # Estadísticas
        with st.expander("📋 Estadísticas descriptivas"):
            st.dataframe(df.describe())

# Mostrar ambos sensores
mostrar_sensor("DHT22", consultas["DHT22"], col1)
mostrar_sensor("MPU6050", consultas["MPU6050"], col2)
import os
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Cargar variables de entorno ---
load_dotenv()

INFLUXDB_URL = os.getenv("INFLUXDB_URL")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

# --- Configuración de la página ---
st.set_page_config(page_title="📊 Tablero de Digitalización de Planta", layout="wide")

# --- Estilos personalizados ---
st.markdown("""
    <style>
        body {
            color: black;
            background-color: white;
        }
        .main {
            background-color: white;
            color: black;
        }
        h1, h2, h3, h4 {
            color: black !important;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stPlotlyChart {
            border: 1px solid #0A7B36;
            border-radius: 15px;
            padding: 15px;
            background-color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- Título principal ---
st.title("📊 Tablero de Digitalización de Planta")
st.write("Visualización de datos en tiempo real desde InfluxDB.")

# --- Conexión a InfluxDB ---
try:
    client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
    query_api = client.query_api()
except Exception as e:
    st.error(f"Error de conexión con InfluxDB: {e}")
    st.stop()

# --- Filtros ---
rango = st.slider("Selecciona el rango de tiempo (días hacia atrás):", min_value=1, max_value=30, value=3)

# --- Consultas por sensor ---
consultas = {
    "DHT22": f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -{rango}d)
            |> filter(fn: (r) => r._measurement == "studio-dht22")
            |> filter(fn: (r) => r._field == "humedad" or r._field == "temperatura" or r._field == "sensacion_termica")
    ''',
    "MPU6050": f'''
        from(bucket: "{INFLUXDB_BUCKET}")
            |> range(start: -{rango}d)
            |> filter(fn: (r) => r._measurement == "mpu6050")
            |> filter(fn: (r) =>
                r._field == "accel_x" or r._field == "accel_y" or r._field == "accel_z" or
                r._field == "gyro_x" or r._field == "gyro_y" or r._field == "gyro_z" or
                r._field == "temperature")
    '''
}

# --- Layout en dos columnas ---
col1, col2 = st.columns(2)

def mostrar_sensor(nombre, query, columna):
    with columna:
        st.subheader(f"📟 Sensor {nombre}")
        try:
            df = query_api.query_data_frame(org=INFLUXDB_ORG, query=query)
            if isinstance(df, list):
                df = pd.concat(df)
        except Exception as e:
            st.error(f"Error al consultar {nombre}: {e}")
            return

        if df.empty:
            st.warning(f"⚠️ No hay datos disponibles para {nombre}.")
            return

        # Limpiar datos
        df = df[["_time", "_field", "_value"]]
        df = df.rename(columns={"_time": "Tiempo", "_field": "Variable", "_value": "Valor"})
        df["Tiempo"] = pd.to_datetime(df["Tiempo"])

        # Graficar cada variable
        for var in df["Variable"].unique():
            sub_df = df[df["Variable"] == var]
            fig = px.line(
                sub_df,
                x="Tiempo",
                y="Valor",
                title=f"{var}",
                template="plotly_white",
                color_discrete_sequence=["#0A7B36"]
            )
            fig.update_layout(
                margin=dict(l=20, r=20, t=40, b=20),
                plot_bgcolor="white",
                paper_bgcolor="white",
                title_font=dict(color="black"),
                font=dict(color="black")
            )
            st.plotly_chart(fig, use_container_width=True)

        # Estadísticas
        with st.expander("📋 Estadísticas descriptivas"):
            st.dataframe(df.describe())

# Mostrar ambos sensores
mostrar_sensor("DHT22", consultas["DHT22"], col1)
mostrar_sensor("MPU6050", consultas["MPU6050"], col2)
