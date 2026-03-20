import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import os
import base64
import tempfile
from gtts import gTTS
import zipfile
from io import BytesIO
from utils.pdf_generator import generar_informe_pdf

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Prototipo Diálisis Peritoneal",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fdf2f8 0%, #fce7f3 100%);
    }
    .main-header {
        background: rgba(255, 255, 255, 0.98);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border: 1px solid #fbcfe8;
    }
    .main-header h1 {
        color: #831843;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    .main-header h2 {
        color: #9d174d;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
    }
    .prototipo-badge {
        background: #ec4899;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        display: inline-block;
        font-weight: bold;
        margin-top: 1rem;
    }
    .advertencia {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .metrica-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        border: 2px solid #f9a8d4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 1rem;
    }
    .metrica-label {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        color: #4a5568;
        margin-bottom: 0.2rem;
    }
    .metrica-grande {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
        color: #831843;
        line-height: 1.2;
    }
    .boton-menu {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        margin: 0.5rem 0;
        border: 2px solid #f9a8d4;
        width: 100%;
        font-size: 1.2rem !important;
        font-weight: bold;
        color: #831843;
    }
    .boton-menu:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(249, 168, 212, 0.3);
        background: #fdf2f8;
        border-color: #f472b6;
    }
    .footer {
        text-align: center;
        color: #831843;
        margin-top: 2rem;
        opacity: 0.9;
        font-size: 1rem !important;
    }
    .stButton button {
        font-size: 1.1rem !important;
        padding: 0.75rem 1rem !important;
        font-weight: 500 !important;
    }
    .stSelectbox div[data-baseweb="select"] span,
    .stNumberInput input,
    .stDateInput input,
    .stTimeInput input,
    .stTextArea textarea {
        font-size: 1.1rem !important;
    }
    .stRadio label, .stCheckbox label {
        font-size: 1.1rem !important;
    }
    div[data-testid="metric-container"] {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #fbcfe8;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stForm {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #fbcfe8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .stAlert {
        font-size: 1.1rem !important;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 1.1rem !important;
    }
    .stDataFrame {
        font-size: 1rem !important;
    }
    /* Botón de manual pequeño */
    .manual-btn {
        background: #f9a8d4;
        color: #831843;
        border: none;
        border-radius: 50px;
        padding: 0.3rem 0.8rem;
        font-size: 0.9rem !important;
        font-weight: bold;
        cursor: pointer;
        margin-top: 0.5rem;
        transition: all 0.3s;
    }
    .manual-btn:hover {
        background: #ec4899;
        color: white;
    }
    /* Tarjeta de autor */
    .autor-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #ec4899;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .autor-nombre {
        font-size: 1.3rem;
        font-weight: bold;
        color: #831843;
    }
    .autor-titulo {
        font-size: 1rem;
        color: #4a5568;
        font-style: italic;
        margin-bottom: 1rem;
    }
    .manual-section {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid #f9a8d4;
        margin: 1rem 0;
    }
    .manual-section h4 {
        color: #831843;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# INICIALIZACIÓN DE DATOS EN MEMORIA (session_state)
# ============================================================
if "registros_manual" not in st.session_state:
    st.session_state.registros_manual = []

if "registros_cicladora" not in st.session_state:
    st.session_state.registros_cicladora = []

if "contador_id" not in st.session_state:
    st.session_state.contador_id = 1

if "pagina" not in st.session_state:
    st.session_state.pagina = "principal"

if "mostrar_manual" not in st.session_state:
    st.session_state.mostrar_manual = False

if "mostrar_autor" not in st.session_state:
    st.session_state.mostrar_autor = False

# ============================================================
# BARRA LATERAL - INFORMACIÓN Y ESTADO
# ============================================================
with st.sidebar:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 🧪 Prototipo")
    with col2:
        # Botón pequeño de manual
        if st.button("❓", key="manual_btn", help="Manual de uso"):
            st.session_state.mostrar_manual = not st.session_state.mostrar_manual
            if st.session_state.mostrar_manual:
                st.session_state.mostrar_autor = False
            st.rerun()
    
    st.markdown("""
    <div class="advertencia">
        ⚠️ <strong>Modo prueba</strong><br>
        Datos temporales en memoria.<br>
        Al recargar la página se pierden.
    </div>
    """, unsafe_allow_html=True)
    
    # Botón para ver reseña del autor (más pequeño)
    if st.button("👤 Sobre el autor", key="autor_btn", use_container_width=True):
        st.session_state.mostrar_autor = not st.session_state.mostrar_autor
        if st.session_state.mostrar_autor:
            st.session_state.mostrar_manual = False
        st.rerun()
    
    st.markdown("### 📊 Estadísticas")
    total_manuales = len(st.session_state.registros_manual)
    total_cicladoras = len(st.session_state.registros_cicladora)
    st.metric("Registros Manuales", total_manuales)
    st.metric("Registros Cicladora", total_cicladoras)
    st.metric("Total", total_manuales + total_cicladoras)
    
    st.markdown("---")
    st.markdown(f"🕒 **Hora actual:** {datetime.now().strftime('%H:%M')}")

# ============================================================
# SECCIÓN DE MANUAL DE USO (emergente en página principal)
# ============================================================
if st.session_state.mostrar_manual:
    with st.container():
        st.markdown("""
        <div class="manual-section">
            <h4>📘 MANUAL DE USO RÁPIDO</h4>
            <p><strong>Para pacientes y personal de salud</strong></p>
            <ul>
                <li><strong>➕ NUEVO REGISTRO:</strong> Ingresa fecha, hora, tipo de diálisis (Manual o Cicladora) y los pesos/volúmenes correspondientes.</li>
                <li><strong>✏️ MODIFICAR:</strong> Corrige datos de un registro existente.</li>
                <li><strong>🗑️ ELIMINAR:</strong> Borra un registro que ya no necesites.</li>
                <li><strong>📄 INFORME PDF:</strong> Genera reportes con gráficos y tabla de datos del período seleccionado.</li>
                <li><strong>📊 VER REGISTROS:</strong> Consulta el historial completo con filtros por fecha.</li>
                <li><strong>🤖 GUÍA CICLADORA:</strong> Asistente paso a paso para usar la máquina Baxter.</li>
            </ul>
            <p><em>⚠️ Los datos son temporales (solo en memoria). Úsalo para práctica o demostración.</em></p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# SECCIÓN DE RESEÑA DEL AUTOR
# ============================================================
if st.session_state.mostrar_autor:
    with st.container():
        st.markdown("""
        <div class="autor-card">
            <div class="autor-nombre">👤 Willer Gianni Torrico Arispe</div>
            <div class="autor-titulo">Ingeniero Agrícola | MSc en Gestión de Recursos Hídricos | Especialista GIS y Ciencia de Datos</div>
            <p><strong>📍 Ubicación:</strong> Cochabamba, Bolivia | Buenos Aires, Argentina</p>
            <p><strong>📧 Email:</strong> wtorrico@gmail.com</p>
            <p><strong>🔗 LinkedIn:</strong> linkedin.com/in/willer-gianni-torrico-arispe</p>
            <p><strong>💼 Experiencia destacada:</strong> Consultor para GIZ, Banco Mundial, GreenLAC, ENDE, e INIAF. Más de 10 años en análisis geoespacial, evaluación de impacto ambiental y diseño de sistemas de riego.</p>
            <p><strong>📚 Formación:</strong> Maestría en Gestión Integral de Recursos Hídricos (UMSS), Diplomados en IA aplicada a educación, Diseño hidráulico y SIG. Certificado por IBM en Data Science.</p>
            <p><strong>🛠️ Habilidades:</strong> Python, R, SQL, QGIS, ArcGIS, Power BI, Evaluación de Impacto Ambiental.</p>
            <p><em>Esta app fue desarrollada como prototipo de demostración para apoyo en registros de diálisis peritoneal.</em></p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# FUNCIONES DE UTILIDAD (igual que antes)
# ============================================================
def get_proximo_id():
    current = st.session_state.contador_id
    st.session_state.contador_id += 1
    return current

def get_ultimo_registro_manual():
    if st.session_state.registros_manual:
        return st.session_state.registros_manual[-1]
    return None

def insert_registro_manual(datos):
    registro = {
        'id': get_proximo_id(),
        'fecha': datos['fecha'],
        'hora': datos['hora'],
        'concentracion': datos['concentracion'],
        'peso_bolsa_llena_kg': datos['peso_llena'],
        'peso_bolsa_vacia_kg': datos['peso_vacia'],
        'peso_bolsa_drenaje_kg': datos['peso_drenaje'],
        'observaciones': datos['observaciones']
    }
    registro['volumen_infundido_ml'] = (registro['peso_bolsa_llena_kg'] - registro['peso_bolsa_vacia_kg']) * 1000
    registro['volumen_drenado_ml'] = registro['peso_bolsa_drenaje_kg'] * 1000
    
    ultimo = get_ultimo_registro_manual()
    if ultimo:
        registro['balance_ml'] = registro['volumen_drenado_ml'] - ultimo.get('volumen_infundido_ml', 0)
    else:
        registro['balance_ml'] = registro['volumen_drenado_ml'] - registro['volumen_infundido_ml']
    
    st.session_state.registros_manual.append(registro)
    return registro

def insert_registro_cicladora(datos):
    hora_inicio = datetime.strptime(datos['hora_inicio'], "%H:%M:%S").time()
    hora_fin = datetime.strptime(datos['hora_fin'], "%H:%M:%S").time()
    
    inicio_dt = datetime.combine(datetime.today(), hora_inicio)
    fin_dt = datetime.combine(datetime.today(), hora_fin)
    if fin_dt < inicio_dt:
        fin_dt += timedelta(days=1)
    horas_totales = (fin_dt - inicio_dt).total_seconds() / 3600
    
    registro = {
        'id': get_proximo_id(),
        'fecha': datos['fecha'],
        'hora_inicio': datos['hora_inicio'],
        'hora_fin': datos['hora_fin'],
        'vol_drenaje_inicial_ml': datos['drenaje_inicial'],
        'uf_total_cicladora_ml': datos['uf_total'],
        'tiempo_permanencia_promedio_min': datos['tiempo_permanencia'],
        'tiempo_perdido_min': datos['tiempo_perdido'],
        'numero_ciclos_completados': datos['num_ciclos'],
        'concentracion_bolsa1': datos['concentracion1'],
        'concentracion_bolsa2': datos['concentracion2'],
        'observaciones': datos['observaciones'],
        'eficiencia_ml_por_hora': datos['uf_total'] / horas_totales if horas_totales > 0 else 0
    }
    
    st.session_state.registros_cicladora.append(registro)
    return registro

def get_registros_fecha(fecha_inicio, fecha_fin):
    registros = []
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
    
    for r in st.session_state.registros_manual:
        fecha_reg = datetime.strptime(r['fecha'], "%Y-%m-%d").date()
        if inicio <= fecha_reg <= fin:
            registros.append({
                'id': r['id'],
                'fecha': r['fecha'],
                'hora': r['hora'],
                'tipo_dialisis': 'Manual',
                'color_bolsa': r['concentracion'],
                'volumen_infundido_ml': r['volumen_infundido_ml'],
                'volumen_drenado_ml': r['volumen_drenado_ml'],
                'uf_recambio_manual_ml': r['balance_ml'],
                'observaciones': r['observaciones']
            })
    
    for r in st.session_state.registros_cicladora:
        fecha_reg = datetime.strptime(r['fecha'], "%Y-%m-%d").date()
        if inicio <= fecha_reg <= fin:
            registros.append({
                'id': r['id'],
                'fecha': r['fecha'],
                'hora_inicio': r['hora_inicio'],
                'hora_fin': r['hora_fin'],
                'tipo_dialisis': 'Cicladora',
                'uf_total_cicladora_ml': r['uf_total_cicladora_ml'],
                'eficiencia_ml_por_hora': r['eficiencia_ml_por_hora'],
                'concentracion_bolsa1': r['concentracion_bolsa1'],
                'concentracion_bolsa2': r['concentracion_bolsa2'],
                'vol_drenaje_inicial_ml': r['vol_drenaje_inicial_ml'],
                'observaciones': r['observaciones']
            })
    
    registros.sort(key=lambda x: x['fecha'], reverse=True)
    return registros

def get_estadisticas_periodo(fecha_inicio, fecha_fin):
    registros = get_registros_fecha(fecha_inicio, fecha_fin)
    
    if not registros:
        return None
    
    dias = {}
    for reg in registros:
        fecha = reg['fecha']
        if fecha not in dias:
            dias[fecha] = {
                'uf_cicladora': 0,
                'uf_manual': 0,
                'num_manuales': 0,
                'num_cicladoras': 0
            }
        
        if reg['tipo_dialisis'] == 'Cicladora':
            dias[fecha]['uf_cicladora'] += reg.get('uf_total_cicladora_ml', 0)
            dias[fecha]['num_cicladoras'] += 1
        else:
            dias[fecha]['uf_manual'] += reg.get('uf_recambio_manual_ml', 0)
            dias[fecha]['num_manuales'] += 1
    
    uf_por_dia = []
    fechas_lista = []
    for fecha, datos in dias.items():
        total_uf = datos['uf_cicladora'] + datos['uf_manual']
        uf_por_dia.append(total_uf)
        fechas_lista.append(fecha)
    
    return {
        'total_dias': len(dias),
        'total_registros': len(registros),
        'total_manuales': sum(d['num_manuales'] for d in dias.values()),
        'total_cicladoras': sum(d['num_cicladoras'] for d in dias.values()),
        'uf_total_periodo': sum(uf_por_dia),
        'uf_promedio_dia': sum(uf_por_dia) / len(dias) if dias else 0,
        'dias_con_uf_negativa': sum(1 for uf in uf_por_dia if uf < 0),
        'dias_con_uf_positiva': sum(1 for uf in uf_por_dia if uf > 0),
        'uf_max': max(uf_por_dia) if uf_por_dia else 0,
        'uf_min': min(uf_por_dia) if uf_por_dia else 0,
        'uf_cicladora_total': sum(d['uf_cicladora'] for d in dias.values()),
        'uf_manual_total': sum(d['uf_manual'] for d in dias.values()),
        'dias': dias,
        'uf_por_dia': uf_por_dia,
        'fechas': fechas_lista
    }

def update_registro_manual(registro_id, datos):
    for i, reg in enumerate(st.session_state.registros_manual):
        if reg['id'] == registro_id:
            reg['fecha'] = datos['fecha']
            reg['hora'] = datos['hora']
            reg['concentracion'] = datos['concentracion']
            reg['peso_bolsa_llena_kg'] = datos['peso_bolsa_llena_kg']
            reg['peso_bolsa_vacia_kg'] = datos['peso_bolsa_vacia_kg']
            reg['peso_bolsa_drenaje_kg'] = datos['peso_bolsa_drenaje_kg']
            reg['observaciones'] = datos['observaciones']
            
            reg['volumen_infundido_ml'] = (reg['peso_bolsa_llena_kg'] - reg['peso_bolsa_vacia_kg']) * 1000
            reg['volumen_drenado_ml'] = reg['peso_bolsa_drenaje_kg'] * 1000
            reg['balance_ml'] = datos['balance_ml']
            
            return reg
    return None

def update_registro_cicladora(registro_id, datos):
    for i, reg in enumerate(st.session_state.registros_cicladora):
        if reg['id'] == registro_id:
            reg['fecha'] = datos['fecha']
            reg['hora_inicio'] = datos['hora_inicio']
            reg['hora_fin'] = datos['hora_fin']
            reg['vol_drenaje_inicial_ml'] = datos['vol_drenaje_inicial_ml']
            reg['uf_total_cicladora_ml'] = datos['uf_total_cicladora_ml']
            reg['tiempo_permanencia_promedio_min'] = datos['tiempo_permanencia_promedio_min']
            reg['tiempo_perdido_min'] = datos['tiempo_perdido_min']
            reg['numero_ciclos_completados'] = datos['numero_ciclos_completados']
            reg['concentracion_bolsa1'] = datos['concentracion_bolsa1']
            reg['concentracion_bolsa2'] = datos['concentracion_bolsa2']
            reg['observaciones'] = datos['observaciones']
            
            inicio_dt = datetime.combine(datetime.today(), datetime.strptime(reg['hora_inicio'], "%H:%M:%S").time())
            fin_dt = datetime.combine(datetime.today(), datetime.strptime(reg['hora_fin'], "%H:%M:%S").time())
            if fin_dt < inicio_dt:
                fin_dt += timedelta(days=1)
            horas_totales = (fin_dt - inicio_dt).total_seconds() / 3600
            reg['eficiencia_ml_por_hora'] = reg['uf_total_cicladora_ml'] / horas_totales if horas_totales > 0 else 0
            
            return reg
    return None

def delete_registro(registro_id, tipo):
    if tipo == 'Manual':
        st.session_state.registros_manual = [r for r in st.session_state.registros_manual if r['id'] != registro_id]
    else:
        st.session_state.registros_cicladora = [r for r in st.session_state.registros_cicladora if r['id'] != registro_id]
    return True

# ============================================================
# ENCABEZADO PRINCIPAL
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🧪 Prototipo de Registro</h1>
    <h2>Diálisis Peritoneal</h2>
    <span class="prototipo-badge">Versión de Demostración - Sin Base de Datos</span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# MENÚ PRINCIPAL
# ============================================================
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("➕ NUEVO REGISTRO", use_container_width=True):
        st.session_state.pagina = "nuevo"
        st.session_state.mostrar_manual = False
        st.session_state.mostrar_autor = False
    if st.button("✏️ MODIFICAR", use_container_width=True):
        st.session_state.pagina = "modificar"
        st.session_state.mostrar_manual = False
        st.session_state.mostrar_autor = False

with col2:
    if st.button("🗑️ ELIMINAR", use_container_width=True):
        st.session_state.pagina = "eliminar"
        st.session_state.mostrar_manual = False
        st.session_state.mostrar_autor = False
    if st.button("📄 INFORME PDF", use_container_width=True):
        st.session_state.pagina = "informe"
        st.session_state.mostrar_manual = False
        st.session_state.mostrar_autor = False

with col3:
    if st.button("📊 VER REGISTROS", use_container_width=True):
        st.session_state.pagina = "ver"
        st.session_state.mostrar_manual = False
        st.session_state.mostrar_autor = False
    if st.button("🤖 GUÍA CICLADORA", use_container_width=True):
        st.session_state.pagina = "ayuda_cicladora"
        st.session_state.paso_cicladora = 1
        st.session_state.mostrar_manual = False
        st.session_state.mostrar_autor = False

# ============================================================
# PÁGINA: PRINCIPAL (por defecto)
# ============================================================
if st.session_state.pagina == "principal":
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h3>Selecciona una opción del menú superior</h3>
        <p style="color: #666; margin-top: 2rem;">
            Este es un prototipo de demostración para registro de diálisis peritoneal.<br>
            Los datos se almacenan temporalmente en memoria y se pierden al recargar la página.
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PÁGINA: NUEVO REGISTRO
# ============================================================
if st.session_state.pagina == "nuevo":
    st.markdown("---")
    st.subheader("➕ Nuevo Registro de Diálisis")
    
    tipo = st.radio("Seleccionar tipo:", ["Manual", "Cicladora"], horizontal=True)
    
    if tipo == "Manual":
        if "unidad_manual" not in st.session_state:
            st.session_state.unidad_manual = "Kilogramos (kg)"
        
        unidad = st.radio(
            "Unidad de peso:",
            ["Kilogramos (kg)", "Gramos (g)"],
            horizontal=True,
            key="unidad_manual_selector"
        )
        st.session_state.unidad_manual = unidad
        
        with st.form("form_manual"):
            st.markdown("### 🖐️ Diálisis Manual")
            
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("Fecha", datetime.now(), format="DD/MM/YYYY")
            with col2:
                hora_time = st.time_input("Hora", datetime.now().time(), step=60)
                hora_str = hora_time.strftime("%H:%M:%S")
            
            concentracion = st.selectbox("Concentración (Color)", ["Amarillo", "Verde", "Rojo"])
            
            peso_llena_kg = 0
            peso_vacia_kg = 0
            peso_drenaje_kg = 0
            
            if st.session_state.unidad_manual == "Kilogramos (kg)":
                st.markdown("#### ⚖️ Pesos (en kilogramos)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    peso_llena = st.number_input("Peso bolsa llena (infusión)", min_value=0.0, step=0.1, format="%.3f", value=2.0, key="peso_llena_kg")
                    peso_llena_kg = peso_llena
                    st.caption("Bolsa de solución NUEVA")
                with col2:
                    peso_vacia = st.number_input("Peso bolsa vacía (opcional)", min_value=0.0, step=0.1, format="%.3f", value=0.0, key="peso_vacia_kg")
                    peso_vacia_kg = peso_vacia
                    st.caption("Bolsa después de infundir")
                with col3:
                    peso_drenaje = st.number_input("Peso bolsa drenaje", min_value=0.0, step=0.1, format="%.3f", value=2.2, key="peso_drenaje_kg")
                    peso_drenaje_kg = peso_drenaje
                    st.caption("Bolsa con líquido drenado")
            else:
                st.markdown("#### ⚖️ Pesos (en gramos)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    peso_llena_g = st.number_input("Peso bolsa llena (infusión) (g)", min_value=0, step=10, format="%d", value=2000, key="peso_llena_g")
                    peso_llena_kg = peso_llena_g / 1000
                    st.caption(f"Equivale a {peso_llena_kg:.3f} kg")
                with col2:
                    peso_vacia_g = st.number_input("Peso bolsa vacía (opcional) (g)", min_value=0, step=10, format="%d", value=0, key="peso_vacia_g")
                    peso_vacia_kg = peso_vacia_g / 1000
                    st.caption(f"Equivale a {peso_vacia_kg:.3f} kg")
                with col3:
                    peso_drenaje_g = st.number_input("Peso bolsa drenaje (g)", min_value=0, step=10, format="%d", value=2200, key="peso_drenaje_g")
                    peso_drenaje_kg = peso_drenaje_g / 1000
                    st.caption(f"Equivale a {peso_drenaje_kg:.3f} kg")
            
            if peso_llena_kg > 0:
                vol_infundido = (peso_llena_kg - peso_vacia_kg) * 1000
                vol_drenado = peso_drenaje_kg * 1000
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Volumen infundido", f"{vol_infundido:.0f} ml")
                with col2:
                    st.metric("Volumen drenado", f"{vol_drenado:.0f} ml")
            
            observaciones = st.text_area("📝 Observaciones")
            
            if st.form_submit_button("💾 Guardar Registro Manual", use_container_width=True):
                datos = {
                    'fecha': fecha.strftime("%Y-%m-%d"),
                    'hora': hora_str,
                    'concentracion': concentracion,
                    'peso_llena': peso_llena_kg,
                    'peso_vacia': peso_vacia_kg,
                    'peso_drenaje': peso_drenaje_kg,
                    'observaciones': observaciones
                }
                insert_registro_manual(datos)
                st.success("✅ Registro manual guardado (memoria temporal)")
                st.balloons()
                st.session_state.pagina = "principal"
                st.rerun()
    
    else:  # Cicladora
        with st.form("form_cicladora"):
            st.markdown("### 🤖 Diálisis con Cicladora")
            st.info("Registra los datos que muestra la máquina al final del tratamiento")
            
            col1, col2 = st.columns(2)
            with col1:
                fecha = st.date_input("Fecha", datetime.now(), format="DD/MM/YYYY")
            with col2:
                st.markdown("")
            
            st.markdown("#### ⏰ Horario del tratamiento")
            col_h1, col_h2 = st.columns(2)
            with col_h1:
                hora_inicio = st.time_input("Hora inicio", datetime.now().time(), step=60)
            with col_h2:
                hora_fin = st.time_input("Hora fin", (datetime.now() + timedelta(hours=8)).time(), step=60)
            
            hora_inicio_str = hora_inicio.strftime("%H:%M:%S")
            hora_fin_str = hora_fin.strftime("%H:%M:%S")
            
            st.markdown("#### 🧴 BOLSAS UTILIZADAS")
            col1, col2 = st.columns(2)
            with col1:
                conc1 = st.selectbox("Color Bolsa 1", ["Amarillo", "Verde", "Rojo"], key="conc1")
            with col2:
                conc2 = st.selectbox("Color Bolsa 2", ["Amarillo", "Verde", "Rojo"], key="conc2")
            
            st.markdown("#### 📊 DATOS DE LA MÁQUINA")
            col1, col2 = st.columns(2)
            with col1:
                drenaje_inicial = st.number_input("Drenaje inicial (ml)", min_value=0, step=50)
                uf_total = st.number_input("UF Total (ml)", min_value=0, step=50)
                tiempo_permanencia = st.number_input("Tiempo permanencia promedio (min)", min_value=0, step=5)
            with col2:
                tiempo_perdido = st.number_input("Tiempo perdido (min)", min_value=0, step=5)
                num_ciclos = st.number_input("Número de ciclos", min_value=1, step=1, value=4)
            
            observaciones = st.text_area("📝 Observaciones")
            
            if st.form_submit_button("💾 Guardar Registro Cicladora", use_container_width=True):
                datos = {
                    'fecha': fecha.strftime("%Y-%m-%d"),
                    'hora_inicio': hora_inicio_str,
                    'hora_fin': hora_fin_str,
                    'drenaje_inicial': drenaje_inicial,
                    'uf_total': uf_total,
                    'tiempo_permanencia': tiempo_permanencia,
                    'tiempo_perdido': tiempo_perdido,
                    'num_ciclos': num_ciclos,
                    'concentracion1': conc1,
                    'concentracion2': conc2,
                    'observaciones': observaciones
                }
                insert_registro_cicladora(datos)
                st.success("✅ Registro de cicladora guardado (memoria temporal)")
                st.balloons()
                st.session_state.pagina = "principal"
                st.rerun()
    
    if st.button("← Volver al menú"):
        st.session_state.pagina = "principal"
        st.rerun()

# ============================================================
# PÁGINA: VER REGISTROS
# ============================================================
if st.session_state.pagina == "ver":
    st.markdown("---")
    st.subheader("📊 Historial de Registros")
    
    registros = get_registros_fecha("2000-01-01", "2100-01-01")
    
    if registros:
        df = pd.DataFrame(registros)
        df['fecha'] = pd.to_datetime(df['fecha'])
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_min = df['fecha'].min().date()
            fecha_max = df['fecha'].max().date()
            fecha_inicio = st.date_input("Fecha inicio", fecha_min, format="DD/MM/YYYY")
        with col2:
            fecha_fin = st.date_input("Fecha fin", fecha_max, format="DD/MM/YYYY")
        
        mask = (df['fecha'].dt.date >= fecha_inicio) & (df['fecha'].dt.date <= fecha_fin)
        df_filtrado = df[mask]
        
        if not df_filtrado.empty:
            tab1, tab2 = st.tabs(["📋 Manual", "🤖 Cicladora"])
            
            with tab1:
                df_manual = df_filtrado[df_filtrado['tipo_dialisis'] == 'Manual'].copy()
                if not df_manual.empty:
                    df_show = df_manual[['fecha', 'hora', 'color_bolsa', 'volumen_infundido_ml', 
                                         'volumen_drenado_ml', 'uf_recambio_manual_ml', 'observaciones']].copy()
                    df_show['fecha'] = df_show['fecha'].dt.strftime('%d/%m/%Y')
                    df_show['hora'] = df_show['hora'].str[:5]
                    df_show.columns = ['Fecha', 'Hora', 'Color', 'Infundido', 'Drenado', 'Balance', 'Obs']
                    
                    def highlight_balance(val):
                        if pd.notna(val) and val < 0:
                            return 'color: red; font-weight: bold'
                        return ''
                    
                    st.dataframe(
                        df_show.style.applymap(highlight_balance, subset=['Balance']),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("No hay registros manuales en este período")
            
            with tab2:
                df_ciclo = df_filtrado[df_filtrado['tipo_dialisis'] == 'Cicladora'].copy()
                if not df_ciclo.empty:
                    df_show = df_ciclo[['fecha', 'hora_inicio', 'hora_fin', 'uf_total_cicladora_ml',
                                       'eficiencia_ml_por_hora', 'concentracion_bolsa1', 'concentracion_bolsa2',
                                       'vol_drenaje_inicial_ml', 'observaciones']].copy()
                    df_show['fecha'] = df_show['fecha'].dt.strftime('%d/%m/%Y')
                    df_show['hora_inicio'] = df_show['hora_inicio'].str[:5]
                    df_show['hora_fin'] = df_show['hora_fin'].str[:5]
                    df_show.columns = ['Fecha', 'Inicio', 'Fin', 'UF', 'Efic', 'Bolsa1', 'Bolsa2', 'Dren.Ini', 'Obs']
                    
                    st.dataframe(df_show, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay registros de cicladora en este período")
            
            # Gráficos
            st.markdown("### 📈 Análisis del período")
            
            df_diario = df_filtrado.copy()
            df_diario['uf_mostrar'] = df_diario.apply(
                lambda x: x['uf_total_cicladora_ml'] if x['tipo_dialisis'] == 'Cicladora' 
                else x['uf_recambio_manual_ml'], axis=1
            )
            
            df_diario_grouped = df_diario.groupby(df_diario['fecha'].dt.date).agg({
                'uf_mostrar': 'sum',
                'tipo_dialisis': lambda x: 'Mixto' if (x == 'Cicladora').any() and (x == 'Manual').any() 
                                             else ('Cicladora' if (x == 'Cicladora').all() else 'Manual')
            }).reset_index()
            df_diario_grouped.columns = ['fecha', 'uf_total_dia', 'tipo_dia']
            
            fig = px.line(df_diario_grouped, x='fecha', y='uf_total_dia',
                         title='Evolución de UF por Día',
                         labels={'uf_total_dia': 'UF (ml)', 'fecha': 'Fecha'})
            fig.add_hline(y=0, line_dash="dash", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay registros en el período seleccionado")
    else:
        st.info("No hay registros aún")
    
    if st.button("← Volver al menú"):
        st.session_state.pagina = "principal"
        st.rerun()

# ============================================================
# PÁGINA: MODIFICAR REGISTRO
# ============================================================
if st.session_state.pagina == "modificar":
    st.markdown("---")
    st.subheader("✏️ Modificar Registro")
    
    if "modificar_paso" not in st.session_state:
        st.session_state.modificar_paso = "seleccionar"
        st.session_state.modificar_id = None
        st.session_state.modificar_tipo = None
    
    if st.session_state.modificar_paso == "seleccionar":
        registros = get_registros_fecha("2000-01-01", "2100-01-01")
        if registros:
            opciones = {}
            for r in registros:
                fecha = r['fecha'][-5:] if r['fecha'] else ''
                hora = r.get('hora', '')[:5] if r.get('hora') else ''
                if not hora and r.get('hora_inicio'):
                    hora = r.get('hora_inicio', '')[:5]
                tipo = r['tipo_dialisis']
                
                if tipo == 'Cicladora':
                    uf = r.get('uf_total_cicladora_ml', 0) or 0
                else:
                    uf = r.get('uf_recambio_manual_ml', 0) or 0
                
                label = f"ID {r['id']} - {fecha} {hora} - {tipo} - UF: {uf:.0f} ml"
                opciones[label] = {'id': r['id'], 'tipo': r['tipo_dialisis']}
            
            seleccion = st.selectbox("Selecciona registro a modificar:", list(opciones.keys()))
            st.session_state.modificar_id = opciones[seleccion]['id']
            st.session_state.modificar_tipo = opciones[seleccion]['tipo']
            
            if st.button("✏️ CONTINUAR CON MODIFICACIÓN", use_container_width=True):
                st.session_state.modificar_paso = "editar"
                st.rerun()
        else:
            st.info("No hay registros para modificar")
            if st.button("← Volver al menú"):
                st.session_state.pagina = "principal"
                st.rerun()
    
    elif st.session_state.modificar_paso == "editar":
        registro_id = st.session_state.modificar_id
        tipo = st.session_state.modificar_tipo
        
        if tipo == "Manual":
            registro = None
            for r in st.session_state.registros_manual:
                if r['id'] == registro_id:
                    registro = r
                    break
            
            if not registro:
                st.error("No se encontró el registro")
                st.session_state.modificar_paso = "seleccionar"
                st.rerun()
            
            if "unidad_mod_manual" not in st.session_state:
                st.session_state.unidad_mod_manual = "Kilogramos (kg)"
            
            st.markdown(f"### ✏️ Editando Registro Manual ID: {registro_id}")
            
            unidad_seleccionada = st.radio(
                "Unidad de peso:",
                ["Kilogramos (kg)", "Gramos (g)"],
                horizontal=True,
                key="unidad_radio_mod"
            )
            st.session_state.unidad_mod_manual = unidad_seleccionada
            
            with st.form("form_modificar_manual"):
                col1, col2 = st.columns(2)
                with col1:
                    nueva_fecha = st.date_input(
                        "Fecha", 
                        datetime.strptime(registro['fecha'], '%Y-%m-%d').date(),
                        format="DD/MM/YYYY"
                    )
                with col2:
                    nueva_hora_time = st.time_input(
                        "Hora",
                        datetime.strptime(registro['hora'], '%H:%M:%S').time(),
                        step=60
                    )
                
                nueva_concentracion = st.selectbox(
                    "Concentración (Color)",
                    ["Amarillo", "Verde", "Rojo"],
                    index=["Amarillo", "Verde", "Rojo"].index(registro['concentracion'])
                )
                
                peso_llena_actual = float(registro['peso_bolsa_llena_kg'])
                peso_vacia_actual = float(registro['peso_bolsa_vacia_kg'] or 0)
                peso_drenaje_actual = float(registro['peso_bolsa_drenaje_kg'])
                
                peso_llena_kg = peso_llena_actual
                peso_vacia_kg = peso_vacia_actual
                peso_drenaje_kg = peso_drenaje_actual
                
                if st.session_state.unidad_mod_manual == "Kilogramos (kg)":
                    st.markdown("#### ⚖️ Pesos (en kilogramos)")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        peso_llena = st.number_input(
                            "Peso bolsa llena (infusión)",
                            min_value=0.0, step=0.1, format="%.3f",
                            value=peso_llena_actual,
                            key="mod_peso_llena_kg"
                        )
                        peso_llena_kg = peso_llena
                        st.caption(f"Actual: {peso_llena_actual:.3f} kg")
                    with col2:
                        peso_vacia = st.number_input(
                            "Peso bolsa vacía (opcional)",
                            min_value=0.0, step=0.1, format="%.3f",
                            value=peso_vacia_actual,
                            key="mod_peso_vacia_kg"
                        )
                        peso_vacia_kg = peso_vacia
                        st.caption(f"Actual: {peso_vacia_actual:.3f} kg")
                    with col3:
                        peso_drenaje = st.number_input(
                            "Peso bolsa drenaje",
                            min_value=0.0, step=0.1, format="%.3f",
                            value=peso_drenaje_actual,
                            key="mod_peso_drenaje_kg"
                        )
                        peso_drenaje_kg = peso_drenaje
                        st.caption(f"Actual: {peso_drenaje_actual:.3f} kg")
                else:
                    st.markdown("#### ⚖️ Pesos (en gramos)")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        peso_llena_g = st.number_input(
                            "Peso bolsa llena (infusión) (g)",
                            min_value=0, step=10, format="%d",
                            value=int(peso_llena_actual * 1000),
                            key="mod_peso_llena_g"
                        )
                        peso_llena_kg = peso_llena_g / 1000
                        st.caption(f"Actual: {int(peso_llena_actual * 1000)} g = {peso_llena_actual:.3f} kg")
                    with col2:
                        peso_vacia_g = st.number_input(
                            "Peso bolsa vacía (opcional) (g)",
                            min_value=0, step=10, format="%d",
                            value=int(peso_vacia_actual * 1000),
                            key="mod_peso_vacia_g"
                        )
                        peso_vacia_kg = peso_vacia_g / 1000
                        st.caption(f"Actual: {int(peso_vacia_actual * 1000)} g = {peso_vacia_actual:.3f} kg")
                    with col3:
                        peso_drenaje_g = st.number_input(
                            "Peso bolsa drenaje (g)",
                            min_value=0, step=10, format="%d",
                            value=int(peso_drenaje_actual * 1000),
                            key="mod_peso_drenaje_g"
                        )
                        peso_drenaje_kg = peso_drenaje_g / 1000
                        st.caption(f"Actual: {int(peso_drenaje_actual * 1000)} g = {peso_drenaje_actual:.3f} kg")
                
                vol_infundido = (peso_llena_kg - peso_vacia_kg) * 1000
                vol_drenado = peso_drenaje_kg * 1000
                
                col1, col2 = st.columns(2)
                with col1:
                    delta_inf = vol_infundido - registro.get('volumen_infundido_ml', 0)
                    st.metric("Volumen infundido", f"{vol_infundido:.0f} ml", delta=f"{delta_inf:.0f}")
                with col2:
                    delta_dren = vol_drenado - registro.get('volumen_drenado_ml', 0)
                    st.metric("Volumen drenado", f"{vol_drenado:.0f} ml", delta=f"{delta_dren:.0f}")
                
                observaciones = st.text_area("📝 Observaciones", value=registro.get('observaciones', ''))
                
                if st.form_submit_button("💾 GUARDAR CAMBIOS", use_container_width=True, type="primary"):
                    ultimo = get_ultimo_registro_manual()
                    
                    if ultimo and ultimo['id'] != registro_id:
                        balance = (peso_drenaje_kg * 1000) - ultimo.get('volumen_infundido_ml', 0)
                    else:
                        balance = (peso_drenaje_kg * 1000) - (peso_llena_kg - peso_vacia_kg) * 1000
                    
                    nueva_hora_str = nueva_hora_time.strftime("%H:%M:%S")
                    
                    datos_actualizados = {
                        'fecha': nueva_fecha.strftime("%Y-%m-%d"),
                        'hora': nueva_hora_str,
                        'concentracion': nueva_concentracion,
                        'peso_bolsa_llena_kg': peso_llena_kg,
                        'peso_bolsa_vacia_kg': peso_vacia_kg,
                        'peso_bolsa_drenaje_kg': peso_drenaje_kg,
                        'balance_ml': balance,
                        'observaciones': observaciones
                    }
                    
                    resultado = update_registro_manual(registro_id, datos_actualizados)
                    if resultado:
                        st.success("✅ Registro modificado correctamente")
                        st.balloons()
                        st.session_state.modificar_paso = "seleccionar"
                        st.session_state.pagina = "principal"
                        st.rerun()
                    else:
                        st.error("No se pudo actualizar el registro")
        
        else:  # Cicladora
            registro = None
            for r in st.session_state.registros_cicladora:
                if r['id'] == registro_id:
                    registro = r
                    break
            
            if not registro:
                st.error("No se encontró el registro")
                st.session_state.modificar_paso = "seleccionar"
                st.rerun()
            
            st.markdown(f"### ✏️ Editando Registro Cicladora ID: {registro_id}")
            
            with st.form("form_modificar_cicladora"):
                col1, col2 = st.columns(2)
                with col1:
                    nueva_fecha = st.date_input(
                        "Fecha",
                        datetime.strptime(registro['fecha'], '%Y-%m-%d').date(),
                        format="DD/MM/YYYY"
                    )
                with col2:
                    hora_inicio_time = st.time_input(
                        "Hora inicio",
                        datetime.strptime(registro['hora_inicio'], '%H:%M:%S').time(),
                        step=60
                    )
                    hora_fin_time = st.time_input(
                        "Hora fin",
                        datetime.strptime(registro['hora_fin'], '%H:%M:%S').time(),
                        step=60
                    )
                
                st.markdown("#### 🧴 BOLSAS UTILIZADAS")
                col1, col2 = st.columns(2)
                with col1:
                    conc1 = st.selectbox(
                        "Color Bolsa 1",
                        ["Amarillo", "Verde", "Rojo"],
                        index=["Amarillo", "Verde", "Rojo"].index(registro.get('concentracion_bolsa1', 'Amarillo'))
                    )
                with col2:
                    conc2 = st.selectbox(
                        "Color Bolsa 2",
                        ["Amarillo", "Verde", "Rojo"],
                        index=["Amarillo", "Verde", "Rojo"].index(registro.get('concentracion_bolsa2', 'Amarillo'))
                    )
                
                st.markdown("#### 📊 DATOS DE LA MÁQUINA")
                col1, col2 = st.columns(2)
                with col1:
                    drenaje_inicial = st.number_input(
                        "Drenaje inicial (ml)",
                        min_value=0, step=50,
                        value=registro.get('vol_drenaje_inicial_ml', 0)
                    )
                    uf_total = st.number_input(
                        "UF Total (ml)",
                        min_value=0, step=50,
                        value=registro.get('uf_total_cicladora_ml', 0)
                    )
                    tiempo_permanencia = st.number_input(
                        "Tiempo permanencia promedio (min)",
                        min_value=0, step=5,
                        value=registro.get('tiempo_permanencia_promedio_min', 0)
                    )
                with col2:
                    tiempo_perdido = st.number_input(
                        "Tiempo perdido (min)",
                        min_value=0, step=5,
                        value=registro.get('tiempo_perdido_min', 0)
                    )
                    num_ciclos = st.number_input(
                        "Número de ciclos",
                        min_value=1, step=1,
                        value=registro.get('numero_ciclos_completados', 4)
                    )
                
                observaciones = st.text_area("📝 Observaciones", value=registro.get('observaciones', ''))
                
                if st.form_submit_button("💾 GUARDAR CAMBIOS", use_container_width=True, type="primary"):
                    hora_inicio_str = hora_inicio_time.strftime("%H:%M:%S")
                    hora_fin_str = hora_fin_time.strftime("%H:%M:%S")
                    
                    datos_actualizados = {
                        'fecha': nueva_fecha.strftime("%Y-%m-%d"),
                        'hora_inicio': hora_inicio_str,
                        'hora_fin': hora_fin_str,
                        'vol_drenaje_inicial_ml': drenaje_inicial,
                        'uf_total_cicladora_ml': uf_total,
                        'tiempo_permanencia_promedio_min': tiempo_permanencia,
                        'tiempo_perdido_min': tiempo_perdido,
                        'numero_ciclos_completados': num_ciclos,
                        'concentracion_bolsa1': conc1,
                        'concentracion_bolsa2': conc2,
                        'observaciones': observaciones
                    }
                    
                    resultado = update_registro_cicladora(registro_id, datos_actualizados)
                    if resultado:
                        st.success("✅ Registro modificado correctamente")
                        st.balloons()
                        st.session_state.modificar_paso = "seleccionar"
                        st.session_state.pagina = "principal"
                        st.rerun()
                    else:
                        st.error("No se pudo actualizar el registro")
    
    if st.button("← Volver al menú principal", use_container_width=True):
        st.session_state.modificar_paso = "seleccionar"
        st.session_state.pagina = "principal"
        st.rerun()

# ============================================================
# PÁGINA: ELIMINAR REGISTRO
# ============================================================
if st.session_state.pagina == "eliminar":
    st.markdown("---")
    st.subheader("🗑️ Eliminar Registro")
    
    registros = get_registros_fecha("2000-01-01", "2100-01-01")
    if registros:
        opciones = {}
        for r in registros:
            fecha = r['fecha'][-5:] if r['fecha'] else ''
            hora = r.get('hora', '')[:5] if r.get('hora') else ''
            if not hora and r.get('hora_inicio'):
                hora = r.get('hora_inicio', '')[:5]
            tipo = r['tipo_dialisis']
            
            if tipo == 'Cicladora':
                uf = r.get('uf_total_cicladora_ml', 0) or 0
            else:
                uf = r.get('uf_recambio_manual_ml', 0) or 0
            
            label = f"ID {r['id']} - {fecha} {hora} - {tipo} - UF: {uf:.0f} ml"
            opciones[label] = {'id': r['id'], 'tipo': r['tipo_dialisis']}
        
        seleccion = st.selectbox("Selecciona registro a eliminar:", list(opciones.keys()))
        registro_id = opciones[seleccion]['id']
        registro_tipo = opciones[seleccion]['tipo']
        
        st.warning(f"¿Estás seguro de eliminar el registro ID {registro_id}?")
        st.info("⚠️ Esta acción no se puede deshacer (en memoria temporal)")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ CONFIRMAR ELIMINACIÓN", type="primary", use_container_width=True):
                delete_registro(registro_id, registro_tipo)
                st.success(f"✅ Registro ID {registro_id} eliminado correctamente")
                st.session_state.pagina = "principal"
                st.rerun()
        with col2:
            if st.button("Cancelar", use_container_width=True):
                st.session_state.pagina = "principal"
                st.rerun()
    else:
        st.info("No hay registros para eliminar")
    
    if st.button("← Volver al menú"):
        st.session_state.pagina = "principal"
        st.rerun()

# ============================================================
# PÁGINA: INFORME PDF
# ============================================================
if st.session_state.pagina == "informe":
    st.markdown("---")
    st.subheader("📄 Generar Informe PDF")
    
    registros = get_registros_fecha("2000-01-01", "2100-01-01")
    
    if registros:
        fechas = [datetime.strptime(r['fecha'], '%Y-%m-%d') for r in registros]
        fecha_min = min(fechas).date()
        fecha_max = max(fechas).date()
        
        col1, col2 = st.columns(2)
        with col1:
            fecha_inicio = st.date_input("📅 Fecha inicio", fecha_min, format="DD/MM/YYYY")
        with col2:
            fecha_fin = st.date_input("📅 Fecha fin", fecha_max, format="DD/MM/YYYY")
        
        tipo_informe = st.radio(
            "📋 Tipo de informe",
            ["completo", "base", "resumen"],
            format_func=lambda x: {
                "completo": "📑 Completo (Base + Resumen)",
                "base": "📊 Solo Base de Datos",
                "resumen": "📈 Solo Resumen"
            }[x],
            horizontal=True
        )
        
        if st.button("📥 Generar PDF", use_container_width=True):
            with st.spinner("Generando informe..."):
                registros_filtrados = get_registros_fecha(
                    fecha_inicio.strftime("%Y-%m-%d"),
                    fecha_fin.strftime("%Y-%m-%d")
                )
                estadisticas = get_estadisticas_periodo(
                    fecha_inicio.strftime("%Y-%m-%d"),
                    fecha_fin.strftime("%Y-%m-%d")
                )
                
                archivos_generados = generar_informe_pdf(
                    registros_filtrados,
                    estadisticas,
                    fecha_inicio.strftime("%d/%m/%Y"),
                    fecha_fin.strftime("%d/%m/%Y"),
                    tipo_informe
                )
                
                if len(archivos_generados) == 1:
                    filename = archivos_generados[0]
                    with open(filename, "rb") as f:
                        pdf_data = f.read()
                    b64_pdf = base64.b64encode(pdf_data).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{filename}">📥 Descargar PDF ({tipo_informe})</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    os.remove(filename)
                else:
                    st.markdown("### 📥 Archivos generados:")
                    col1, col2 = st.columns(2)
                    with col1:
                        filename1 = archivos_generados[0]
                        with open(filename1, "rb") as f:
                            pdf_data = f.read()
                        b64_pdf1 = base64.b64encode(pdf_data).decode()
                        href1 = f'<a href="data:application/octet-stream;base64,{b64_pdf1}" download="{filename1}">📄 Descargar Resumen</a>'
                        st.markdown(href1, unsafe_allow_html=True)
                    with col2:
                        filename2 = archivos_generados[1]
                        with open(filename2, "rb") as f:
                            pdf_data = f.read()
                        b64_pdf2 = base64.b64encode(pdf_data).decode()
                        href2 = f'<a href="data:application/octet-stream;base64,{b64_pdf2}" download="{filename2}">📊 Descargar Base de Datos</a>'
                        st.markdown(href2, unsafe_allow_html=True)
                    
                    zip_buffer = BytesIO()
                    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED) as zip_file:
                        for fname in archivos_generados:
                            zip_file.write(fname, arcname=os.path.basename(fname))
                    zip_data = zip_buffer.getvalue()
                    b64_zip = base64.b64encode(zip_data).decode()
                    fecha_str = fecha_inicio.strftime("%Y%m%d")
                    fecha_fin_str = fecha_fin.strftime("%Y%m%d")
                    href_zip = f'<a href="data:application/zip;base64,{b64_zip}" download="informe_completo_{fecha_str}_{fecha_fin_str}.zip">📦 Descargar ambos (ZIP)</a>'
                    st.markdown(href_zip, unsafe_allow_html=True)
                    
                    for fname in archivos_generados:
                        os.remove(fname)
                
                st.success("✅ Informe(s) generado(s)")
    else:
        st.info("No hay datos para generar informe")
    
    if st.button("← Volver al menú"):
        st.session_state.pagina = "principal"
        st.rerun()


# ============================================================
# PÁGINA: AYUDA CICLADORA (con voz mejorada - AUTO FUNCIONA)
# ============================================================
if st.session_state.pagina == "ayuda_cicladora":
    from gtts import gTTS
    import time
    import hashlib
    import os
    
    # Inicializar estados de voz
    if "voz_automatica" not in st.session_state:
        st.session_state.voz_automatica = False
    
    if "reproduciendo_voz" not in st.session_state:
        st.session_state.reproduciendo_voz = False
    
    if "ultimo_paso_hablado" not in st.session_state:
        st.session_state.ultimo_paso_hablado = None
    
    if "audio_actual_id" not in st.session_state:
        st.session_state.audio_actual_id = None
    
    if "voz_pausada" not in st.session_state:
        st.session_state.voz_pausada = False
    
    # Función para generar un ID único para cada audio
    def generar_audio_id(texto):
        return hashlib.md5(texto.encode()).hexdigest()[:8]
    
    # Función mejorada para generar audio con control total
    def generar_audio_con_controles(texto, idioma='es', autoplay=False, audio_id=None):
        """Genera audio con controles personalizados (sin autoplay duplicado)"""
        try:
            # Crear un ID único para este audio
            if audio_id is None:
                audio_id = generar_audio_id(texto) + "_" + str(int(time.time()))
            
            # Generar archivo de audio
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                tts = gTTS(text=texto, lang=idioma, slow=False)
                tts.save(tmp.name)
                
                # Leer el archivo y codificarlo
                with open(tmp.name, 'rb') as f:
                    audio_bytes = f.read()
                audio_base64 = base64.b64encode(audio_bytes).decode()
                
                # Eliminar archivo temporal
                os.unlink(tmp.name)
                
                # Crear HTML con controles personalizados y JavaScript para control
                autoplay_attr = "autoplay" if autoplay else ""
                
                html = f'''
                <div id="audio-container-{audio_id}" style="margin: 10px 0; display: none;">
                    <audio id="audio-{audio_id}" {autoplay_attr} controls style="width: 100%; height: 40px;">
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                </div>
                <script>
                    (function() {{
                        var audio = document.getElementById('audio-{audio_id}');
                        var container = document.getElementById('audio-container-{audio_id}');
                        
                        // Si hay autoplay, mostrar el contenedor
                        if ({str(autoplay).lower()}) {{
                            container.style.display = 'block';
                        }}
                        
                        // Registrar el audio para control global
                        window.audios = window.audios || {{}};
                        window.audios['{audio_id}'] = {{
                            element: audio,
                            container: container,
                            texto: {repr(texto)},
                            pausada: false
                        }};
                        
                        // Manejar eventos
                        audio.onplay = function() {{
                            window.audioActualId = '{audio_id}';
                        }};
                    }})();
                </script>
                '''
                return html, audio_id
        except Exception as e:
            st.error(f"Error generando audio: {e}")
            return "", None
    
    # Función para detener TODOS los audios
    def detener_todos_audios():
        return '''
        <script>
        (function() {
            if (window.audios) {
                for (var id in window.audios) {
                    var audio = window.audios[id].element;
                    audio.pause();
                    audio.currentTime = 0;
                    window.audios[id].pausada = false;
                }
            }
            window.audioActualId = null;
        })();
        </script>
        '''
    
    # Función para pausar/reanudar
    def pausar_reanudar_audio(pausar=True):
        if pausar:
            return '''
            <script>
            (function() {
                if (window.audioActualId && window.audios[window.audioActualId]) {
                    var audio = window.audios[window.audioActualId].element;
                    audio.pause();
                    window.audios[window.audioActualId].pausada = true;
                }
            })();
            </script>
            '''
        else:
            return '''
            <script>
            (function() {
                if (window.audioActualId && window.audios[window.audioActualId]) {
                    var audio = window.audios[window.audioActualId].element;
                    audio.play();
                    window.audios[window.audioActualId].pausada = false;
                }
            })();
            </script>
            '''
    
    # Función para reproducir un paso específico
    def reproducir_paso(texto, paso_num):
        audio_id = f"paso_{paso_num}_{int(time.time())}"
        html, _ = generar_audio_con_controles(texto, autoplay=True, audio_id=audio_id)
        return html
    
    st.markdown("---")
    st.markdown("## 🤖 GUÍA INTERACTIVA - CICLADORA BAXTER")
    
    # ============================================================
    # CONTROLES DE VOZ MEJORADOS
    # ============================================================
    col_v1, col_v2, col_v3, col_v4, col_v5 = st.columns([1, 1, 1, 1, 2])
    
    with col_v1:
        # Botón AUTO
        if st.button("🔊 AUTO" if not st.session_state.voz_automatica else "🔇 AUTO", 
                    use_container_width=True,
                    key="btn_auto_voz"):
            # Cambiar estado
            nuevo_estado = not st.session_state.voz_automatica
            st.session_state.voz_automatica = nuevo_estado
            
            # Si se desactiva, detener cualquier audio
            if not nuevo_estado:
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.reproduciendo_voz = False
                st.session_state.voz_pausada = False
            
            # Resetear último paso hablado para que el actual pueda hablar si se reactiva
            st.session_state.ultimo_paso_hablado = None
            st.rerun()
    
    with col_v2:
        # Botón STOP
        if st.button("⏹️ STOP", use_container_width=True, key="btn_stop_voz"):
            st.markdown(detener_todos_audios(), unsafe_allow_html=True)
            st.session_state.reproduciendo_voz = False
            st.session_state.voz_pausada = False
            st.success("🔇 Reproducción detenida")
            time.sleep(0.5)
            st.rerun()
    
    with col_v3:
        # Botón PAUSA/REANUDAR
        if not st.session_state.voz_pausada:
            if st.button("⏸️ PAUSA", use_container_width=True, key="btn_pausa_voz"):
                st.markdown(pausar_reanudar_audio(True), unsafe_allow_html=True)
                st.session_state.voz_pausada = True
                st.rerun()
        else:
            if st.button("▶️ REANUDAR", use_container_width=True, key="btn_reanudar_voz"):
                st.markdown(pausar_reanudar_audio(False), unsafe_allow_html=True)
                st.session_state.voz_pausada = False
                st.rerun()
    
    with col_v4:
        # Botón REPETIR PASO
        if st.button("🔁 REPETIR", use_container_width=True, key="btn_repetir_voz"):
            st.session_state.reproduciendo_voz = True
            st.rerun()
    
    with col_v5:
        # Info del estado
        estado_auto = "✅ AUTO ON" if st.session_state.voz_automatica else "⏸️ AUTO OFF"
        estado_pausa = " ⏸️" if st.session_state.voz_pausada else ""
        st.markdown(f"<div style='text-align: right; font-weight: bold;'>{estado_auto}{estado_pausa}</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============================================================
    # BOTONES DE NAVEGACIÓN RÁPIDA
    # ============================================================
    st.markdown("### 🔢 Saltar a paso:")
    cols = st.columns(9)
    pasos = range(1, 10)
    for i, col in enumerate(cols):
        with col:
            if st.button(str(i+1), key=f"paso_btn_{i+1}"):
                # Detener audio actual antes de cambiar
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = i+1
                st.session_state.ultimo_paso_hablado = None  # RESET para que AUTO vuelva a hablar
                st.session_state.reproduciendo_voz = False
                st.session_state.voz_pausada = False
                st.rerun()
    
    # Inicializar paso actual
    if "paso_cicladora" not in st.session_state:
        st.session_state.paso_cicladora = 1
    
    progreso = st.session_state.paso_cicladora / 9
    st.progress(progreso, text=f"Paso {st.session_state.paso_cicladora} de 9")
    
    # ============================================================
    # FUNCIÓN PARA MOSTRAR PASO CON VOZ (AUTO FUNCIONA)
    # ============================================================
    def mostrar_paso_con_voz(numero, titulo, contenido_lista, texto_voz):
        """Muestra un paso y maneja la voz - AUTO funciona en todos los pasos"""
        
        # Si AUTO está activado y este paso NO se ha hablado aún
        if st.session_state.voz_automatica and st.session_state.ultimo_paso_hablado != numero:
            # Reproducir automáticamente
            st.session_state.ultimo_paso_hablado = numero
            st.session_state.reproduciendo_voz = False
            st.session_state.voz_pausada = False
            
            audio_html = reproducir_paso(texto_voz, numero)
            st.markdown(audio_html, unsafe_allow_html=True)
        
        # Si se solicitó REPETIR este paso
        if st.session_state.reproduciendo_voz and st.session_state.ultimo_paso_hablado == numero:
            st.session_state.reproduciendo_voz = False
            st.session_state.voz_pausada = False
            
            audio_html = reproducir_paso(texto_voz, numero)
            st.markdown(audio_html, unsafe_allow_html=True)
        
        # Mostrar contenido del paso
        st.markdown(f"""
        <div class="paso-card" style="background: white; padding: 1.5rem; border-radius: 15px; 
                    border-left: 5px solid #ec4899; margin: 1rem 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h4 style="color: #831843; margin-bottom: 1rem;">{titulo}</h4>
            <ul style="list-style-type: none; padding-left: 0;">
        """, unsafe_allow_html=True)
        
        for item in contenido_lista:
            st.markdown(f"""
            <li style="margin-bottom: 0.8rem; font-size: 1.1rem;">
                {item}
            </li>
            """, unsafe_allow_html=True)
        
        st.markdown("</ul></div>", unsafe_allow_html=True)
    
    # ============================================================
    # PASO 1
    # ============================================================
    if st.session_state.paso_cicladora == 1:
        contenido = [
            "🔌 <strong>Encender:</strong> Botón en la parte POSTERIOR de la máquina",
            "⏳ <strong>Esperar:</strong> Pantalla de inicio",
            "✅ <strong>Presionar:</strong> Botón verde 'GO'",
            "📏 <strong>Seleccionar:</strong> 'Modo volumen pequeño' y presionar verde"
        ]
        texto_voz = "Paso 1: Preparación inicial. Enciende el equipo con el botón en la parte posterior. Espera la pantalla de inicio. Presiona el botón verde GO. Selecciona Modo volumen pequeño y presiona verde nuevamente."
        
        mostrar_paso_con_voz(1, "⚡ PASO 1: PREPARACIÓN INICIAL", contenido, texto_voz)
        
        if st.button("✅ PASO 2", use_container_width=True, key="paso1_next"):
            st.markdown(detener_todos_audios(), unsafe_allow_html=True)
            st.session_state.paso_cicladora = 2
            st.session_state.ultimo_paso_hablado = None  # RESET para que AUTO funcione
            st.session_state.reproduciendo_voz = False
            st.rerun()
    
    # ============================================================
    # PASO 2
    # ============================================================
    elif st.session_state.paso_cicladora == 2:
        contenido = [
            "📎 <strong>Cassette:</strong> Sacar del envoltorio",
            "🔓 <strong>Abrir:</strong> Levantar manija, insertar cassette (parte blanda hacia máquina)",
            "🔒 <strong>Cerrar:</strong> Bajar palanca (debe hacer clic)",
            "🧩 <strong>Organizador:</strong> Acomodar el azul",
            "📌 <strong>Pinzas:</strong> Cerrar las 6",
            "🗑️ <strong>Drenaje:</strong> Línea en bidón vacío"
        ]
        texto_voz = "Paso 2: Colocar el cassette. Saca el cassette del envoltorio. Levanta la manija, inserta el cassette con la parte blanda hacia la máquina. Cierra la puerta. Acomoda el organizador azul. Cierra las 6 pinzas. Coloca la línea de drenaje en el bidón."
        
        mostrar_paso_con_voz(2, "📦 PASO 2: COLOCAR EL CASSETTE", contenido, texto_voz)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ PASO 1", use_container_width=True, key="paso2_prev"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 1
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
        with col2:
            if st.button("✅ PASO 3", use_container_width=True, key="paso2_next"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 3
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
    
    # ============================================================
    # PASO 3
    # ============================================================
    elif st.session_state.paso_cicladora == 3:
        contenido = [
            "⏳ <strong>Test automático:</strong> La máquina se autocomprueba",
            "🧼 <strong>Lavado:</strong> Manos profundamente (40 segundos)",
            "✅ <strong>Preparar:</strong> Bolsas para siguiente paso",
            "🔔 <strong>Aviso:</strong> La máquina pitará al terminar"
        ]
        texto_voz = "Paso 3: Autocomprobación. La máquina hará un test automático. Mientras, lávate las manos profundamente por 40 segundos. Prepara las bolsas para el siguiente paso. La máquina pitará cuando termine."
        
        mostrar_paso_con_voz(3, "🔄 PASO 3: AUTOCOMPROBACIÓN", contenido, texto_voz)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ PASO 2", use_container_width=True, key="paso3_prev"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 2
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
        with col2:
            if st.button("✅ PASO 4", use_container_width=True, key="paso3_next"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 4
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
    
    # ============================================================
    # PASO 4
    # ============================================================
    elif st.session_state.paso_cicladora == 4:
        contenido = [
            "🔵 <strong>Pinzas:</strong> Colocar pinzas azules en bolsas",
            "🔴 <strong>Clamp ROJO:</strong> Aflojar espiga (bolsa superior - se calienta)",
            "⚪ <strong>Clamp BLANCO:</strong> Aflojar espiga (segunda bolsa)",
            "💡 <strong>Importante:</strong> La espiga roja SIEMPRE va a la bolsa de arriba",
            "🖐️ <strong>Conectar:</strong> Romper mariposa y conectar espiga"
        ]
        texto_voz = "Paso 4: Conectar bolsas. Coloca pinzas azules en las bolsas. Afloja la espiga del clamp rojo que va a la bolsa superior que se calienta. Afloja la espiga del clamp blanco para la segunda bolsa. Recuerda, la espiga del clamp rojo siempre va a la bolsa de arriba. Rompe la mariposa y conecta la espiga."
        
        mostrar_paso_con_voz(4, "🧴 PASO 4: CONECTAR BOLSAS", contenido, texto_voz)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ PASO 3", use_container_width=True, key="paso4_prev"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 3
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
        with col2:
            if st.button("✅ PASO 5", use_container_width=True, key="paso4_next"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 5
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
    
    # ============================================================
    # PASO 5
    # ============================================================
    elif st.session_state.paso_cicladora == 5:
        contenido = [
            "🔓 <strong>Pinzas:</strong> Retirar las azules",
            "🚰 <strong>Clamps:</strong> Abrir rojo y blanco",
            "🩺 <strong>Línea paciente:</strong> Abrir clamp",
            "✅ <strong>Continuar:</strong> Presionar botón verde",
            "⏳ <strong>Purgado:</strong> La máquina purga automáticamente (verás burbujas)"
        ]
        texto_voz = "Paso 5: Cebado de líneas. Retira las pinzas azules. Abre los clamp de las bolsas rojo y blanco. Abre el clamp de la línea del paciente. Presiona el botón verde continuar. La máquina purgará las líneas automáticamente y verás burbujas."
        
        mostrar_paso_con_voz(5, "💧 PASO 5: CEVADO DE LÍNEAS", contenido, texto_voz)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ PASO 4", use_container_width=True, key="paso5_prev"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 4
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
        with col2:
            if st.button("✅ PASO 6", use_container_width=True, key="paso5_next"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 6
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
    
    # ============================================================
    # PASO 6
    # ============================================================
    elif st.session_state.paso_cicladora == 6:
        contenido = [
            "🔒 <strong>Clamp:</strong> Cerrar línea paciente",
            "🧴 <strong>Limpieza:</strong> Zona de conexión con alcohol",
            "🔄 <strong>Conexión:</strong> Conectar catéter",
            "🔓 <strong>Abrir:</strong> Catéter y clamp de línea",
            "✅ <strong>Continuar:</strong> Presionar verde",
            "📏 <strong>Volumen:</strong> Seleccionar 'Modo volumen pequeño'"
        ]
        texto_voz = "Paso 6: Conexión al paciente. Cierra el clamp de la línea del paciente. Limpia la zona de conexión con alcohol. Conecta el catéter. Abre el catéter y el clamp de la línea. Presiona verde continuar. Luego selecciona Modo volumen pequeño sin presionar continuar aún."
        
        mostrar_paso_con_voz(6, "👤 PASO 6: CONEXIÓN AL PACIENTE", contenido, texto_voz)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ PASO 5", use_container_width=True, key="paso6_prev"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 5
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
        with col2:
            if st.button("✅ PASO 7", use_container_width=True, key="paso6_next"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 7
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
    
    # ============================================================
    # PASO 7
    # ============================================================
    elif st.session_state.paso_cicladora == 7:
        contenido = [
            "🔍 <strong>Pantalla:</strong> 'Verificar drenaje inicial'",
            "⏳ <strong>Drenaje:</strong> Sale líquido del abdomen",
            "🔄 <strong>Ciclos:</strong> INFUSIÓN → PERMANENCIA → DRENAJE",
            "😴 <strong>Descanso:</strong> Puedes dormir tranquilo",
            "⏰ <strong>Duración:</strong> Varias horas"
        ]
        texto_voz = "Paso 7: Inicio del tratamiento. La máquina mostrará Verificar drenaje inicial. Verás el primer drenaje donde sale líquido del abdomen. Luego comenzarán los ciclos automáticos de infusión, permanencia y drenaje. Puedes dormir tranquilo, la máquina trabajará sola durante varias horas."
        
        mostrar_paso_con_voz(7, "🌙 PASO 7: INICIO DEL TRATAMIENTO", contenido, texto_voz)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ PASO 6", use_container_width=True, key="paso7_prev"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 6
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
        with col2:
            if st.button("✅ PASO 8", use_container_width=True, key="paso7_next"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 8
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
    
    # ============================================================
    # PASO 8
    # ============================================================
    elif st.session_state.paso_cicladora == 8:
        contenido = [
            "🔔 <strong>Pantalla:</strong> 'FIN DE TRATAMIENTO'",
            "⬇️ <strong>Flecha:</strong> Hacia abajo hasta 'DRENAJE MANUAL'",
            "⬅️ <strong>Confirmar:</strong> Flecha izquierda",
            "⏳ <strong>Esperar:</strong> Que termine drenaje",
            "✅ <strong>Continuar:</strong> Presionar verde",
            "🔒 <strong>Cierre:</strong> 'CIERRE CLAMP (TODOS)' - cerrar línea y catéter",
            "✅ <strong>Verde:</strong> Presionar nuevamente"
        ]
        texto_voz = "Paso 8: Al despertar. La máquina mostrará Fin de tratamiento. Presiona flecha hacia abajo hasta ver Drenaje manual. Confirma con flecha izquierda. Espera a que termine el drenaje. Presiona verde continuar. La máquina dirá Cierre clamp todos. Cierra clamp de línea y catéter. Presiona verde nuevamente."
        
        mostrar_paso_con_voz(8, "🌅 PASO 8: AL DESPERTAR", contenido, texto_voz)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ PASO 7", use_container_width=True, key="paso8_prev"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 7
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
        with col2:
            if st.button("✅ PASO 9", use_container_width=True, key="paso8_next"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 9
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
    
    # ============================================================
    # PASO 9
    # ============================================================
    elif st.session_state.paso_cicladora == 9:
        contenido = [
            "🫱 <strong>Desconexión:</strong> 'DESCONECTESE' - aplicar alcohol",
            "✅ <strong>Continuar:</strong> Presionar verde",
            "📤 <strong>Retirar:</strong> 'DESCONECTEME' - sacar cassette",
            "📝 <strong>ANOTAR:</strong> Drenaje inicial, UF total, Tiempo permanencia, Tiempo perdido",
            "🔌 <strong>Apagar:</strong> Botón posterior",
            "🎯 <strong>¡Completado!</strong> Tratamiento finalizado"
        ]
        texto_voz = "Paso 9: Registro de datos. La máquina dirá Desconéctese. Limpia y aplica alcohol. Presiona verde para continuar. La máquina dirá Desconécteme. Retira el cassette. Ahora anota estos valores: Drenaje inicial, Ultrafiltración total, Tiempo medio de permanencia y Tiempo perdido. Apaga el equipo con el botón posterior. Tratamiento completado."
        
        mostrar_paso_con_voz(9, "📋 PASO 9: REGISTRO DE DATOS", contenido, texto_voz)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ PASO 8", use_container_width=True, key="paso9_prev"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 8
                st.session_state.ultimo_paso_hablado = None
                st.rerun()
        with col2:
            if st.button("🏁 FINALIZAR", use_container_width=True, key="paso9_finish"):
                st.markdown(detener_todos_audios(), unsafe_allow_html=True)
                st.session_state.paso_cicladora = 1
                st.session_state.ultimo_paso_hablado = None
                st.session_state.pagina = "principal"
                st.rerun()
    
    # Botón para cerrar guía
    if st.button("❌ Cerrar guía", use_container_width=True, key="btn_cerrar_guia"):
        st.markdown(detener_todos_audios(), unsafe_allow_html=True)
        st.session_state.paso_cicladora = 1
        st.session_state.ultimo_paso_hablado = None
        st.session_state.pagina = "principal"
        st.rerun()
        
# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div class="footer">
    🧪 Prototipo de Registro de Diálisis Peritoneal - Versión de Demostración<br>
    ⚕️ Datos temporales en memoria - Desarrollado por Willer Torrico
</div>
""", unsafe_allow_html=True)
