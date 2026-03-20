import streamlit as st
import requests
from lxml import html
import urllib3

# Configuración de la página (layout="wide" para aprovechar la pantalla completa)
st.set_page_config(page_title="Tu Resuelve Cambiario", page_icon="💱", layout="wide")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_bcv_rate(currency_id):
    url = "https://www.bcv.org.ve/"
    
    # ¡Tus XPaths cortos y blindados!
    if currency_id == "dolar":
        xpath_usar = '//div[@id="dolar"]//strong/text()'
    elif currency_id == "euro":
        xpath_usar = '//div[@id="euro"]//strong/text()'
    else:
        return None
        
    # Cabeceras para simular que somos un navegador real y evitar bloqueos del BCV
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
        
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            tree = html.fromstring(response.content)
            elementos = tree.xpath(xpath_usar)
            
            if elementos:
                # Como el XPath termina en /text(), 'elementos[0]' ya es directamente el texto (" 36,25 ")
                texto_crudo = elementos[0].strip() 
                
                # Reemplazamos la coma por punto
                numero_limpio = texto_crudo.replace(",", ".")
                
                return float(numero_limpio)
        
        return None
    except Exception as e:
        return None

def formato_vzla(monto):
    """Formatea con punto para miles y coma para decimales"""
    return f"{monto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# --- INTERFAZ ---
st.title("💱 ¿Efectivo o Bolívares? 💱")
st.markdown("Compara el costo real de tu compra en divisas.")

# --- SIDEBAR ---
st.sidebar.header("Configuración de Tasas")
opciones_dict = {"Dólar": "dolar", "Euro": "euro"}
seleccion_usuario = st.sidebar.selectbox("Moneda BCV de referencia", list(opciones_dict.keys()))

id_tecnico = opciones_dict[seleccion_usuario]
tasa_bcv = get_bcv_rate(id_tecnico)

# Lógica de Fallback
if tasa_bcv:
    st.sidebar.success(f"Tasa BCV {seleccion_usuario}: Bs. {formato_vzla(tasa_bcv)}")
else:
    st.sidebar.error("⚠️ No se pudo obtener la tasa oficial. Ingresa el valor manualmente.")
    tasa_bcv = st.sidebar.number_input(f"Ingresa Tasa {seleccion_usuario} manualmente", min_value=0.01, value=45.0)

tasa_mercado = st.sidebar.number_input(
    "¿A cuánto vas a vender tus divisas? (Paralelo)", 
    min_value=1.0, 
    value=1.0, 
    step=1.0, 
    format="%.2f"
)

# --- CUERPO PRINCIPAL ---

# Resumen del Mercado (Métricas con Delta)
st.subheader("Resumen del Mercado")
col_m1, col_m2, col_m3 = st.columns(3)

# Cálculo de Spread (Brecha) nominal y porcentual
spread = tasa_mercado - tasa_bcv
spread_pct = (spread / tasa_bcv) * 100 if tasa_bcv > 0 else 0

# Arreglo para que el porcentaje tenga coma en los decimales
spread_pct_str = f"{spread_pct:+.2f}".replace(".", ",")

# Usamos el parámetro 'delta' para mostrar el texto pequeño abajo (verde si es +, rojo si es -)
col_m1.metric("Tasa BCV", f"Bs. {formato_vzla(tasa_bcv)}", f"1 {seleccion_usuario}")
col_m2.metric("Tasa Paralelo", f"Bs. {formato_vzla(tasa_mercado)}", f"1 {seleccion_usuario}")
col_m3.metric("Spread/Brecha", f"Bs. {formato_vzla(spread)}", f"{spread_pct_str}% sobre BCV")

st.divider()

# SECCIÓN DE COMPRA
st.subheader("Datos de la Compra")

col1, col2 = st.columns(2)

with col1:
    # Metemos la selección de base adentro de la columna para que quede alineada
    tipo_precio = st.radio("¿Cómo ingresarás el precio base del producto?", 
                           ["En Dólares ($)", "En Bolívares (Bs.)"], horizontal=True)

    if tipo_precio == "En Dólares ($)":
        precio_ref_usd = st.number_input(
            "Precio del producto ($ BCV)", 
            min_value=0.0, 
            value=0.0, 
            step=1.0, 
            format="%.2f"
        )
        st.caption(f"Valor: **$ {formato_vzla(precio_ref_usd)}**")
    else:
        precio_bs = st.number_input(
            "Precio del producto (Bs.)", 
            min_value=0.0, 
            value=0.0, 
            step=1.0, 
            format="%.2f"
        )
        precio_ref_usd = precio_bs / tasa_bcv if tasa_bcv > 0 else 0
        st.info(f"Monto ingresado: **Bs. {formato_vzla(precio_bs)}**")
        st.caption(f"Equivalente a tasa BCV: **$ {formato_vzla(precio_ref_usd)}**")

with col2:
    # Agregamos la opción de descuento perfectamente alineada con la columna 1
    tipo_oferta = st.radio("¿Cómo te dieron la oferta en efectivo?", 
                           ["Monto directo", "Porcentaje (%)"], horizontal=True)
    
    if tipo_oferta == "Monto directo":
        monto_efectivo_pedido = st.number_input(
            "Oferta si pagas en efectivo ($)", 
            min_value=0.0, 
            value=0.0, 
            step=1.0, 
            format="%.2f"
        )
    else:
        descuento_pct = st.number_input(
            "Porcentaje de descuento (%)", 
            min_value=0.0, 
            max_value=100.0, 
            value=0.0, 
            step=1.0, 
            format="%.2f"
        )
        # Calculamos el monto restando el porcentaje al precio base
        monto_efectivo_pedido = precio_ref_usd - (precio_ref_usd * (descuento_pct / 100))
        
        # APLICAMOS EL FORMATO VZLA AL PORCENTAJE PARA QUE MUESTRE LA COMA
        st.info(f"Descuento de **{formato_vzla(descuento_pct)}%** aplicado.")

    st.caption(f"Monto final a pagar en efectivo: **$ {formato_vzla(monto_efectivo_pedido)}**")

if st.button("🤑 Calcular Decisión Óptima 🤑", use_container_width=True):
    costo_en_bs_pagando_efectivo = monto_efectivo_pedido * tasa_mercado
    costo_en_bs_oficial = precio_ref_usd * tasa_bcv
    
    ahorro_bs = costo_en_bs_oficial - costo_en_bs_pagando_efectivo
    ahorro_usd = ahorro_bs / tasa_mercado
    precio_ideal_usd = (precio_ref_usd * tasa_bcv) / tasa_mercado

    st.divider()
    
    if ahorro_usd > 0.01:
        st.balloons()
        st.success(f"### ✅ ¡ACEPTA LA OFERTA Y PAGA EN EFECTIVO!")
        st.write(f"Te ahorras el equivalente a **${formato_vzla(ahorro_usd)}** en comparación con pagar en bolívares.")
    elif ahorro_usd < -0.01:
        st.error(f"### ❌ ¡RECHAZA LA OFERTA Y PAGA EN BOLÍVARES!")
        st.write(f"Sale mejor vender tus divisas. Ahorras **${formato_vzla(abs(ahorro_usd))}** si pagas en Bs.")

    else:
        st.info("### ⚖️ ES INDIFERENTE")
        st.write("El costo es prácticamente el mismo, puedes elegir cualquiera de las dos formas de pago.")

    st.warning(f"**Nota:** El precio justo en efectivo debería ser **$ {formato_vzla(precio_ideal_usd)}** — donde ambas opciones valen exactamente lo mismo.")

# --- SECCIÓN DE CONTACTO Y PROPINAS MODIFICADA ---
st.divider()
with st.expander("💡 Deja una sugerencia y/o apoya este proyecto"):
    # 1. Dudas y Sugerencias primero
    st.markdown("✉️ **Dudas y Sugerencias**")
    st.markdown("Escríbeme a: [turesuelvecambiario@yopmail.com](mailto:turesuelvecambiario@yopmail.com)")

    st.write("") # Espacio en blanco para separar

    # 2. El texto de invitación
    st.markdown("¿Te ayudé a ahorrar dinero hoy? ¡Considera apoyar esta idea 😁!")

    # 3. El Binance ID al final
    st.markdown("**Binance ID:** `222685335`")

# --- SECCIÓN LEGAL Y PRIVACIDAD ---
with st.expander("⚖️ Aviso Legal y Privacidad"):
    st.markdown("""
    **Privacidad:** Esta página **no recolecta, almacena ni comparte** datos personales. Los cálculos se realizan en tiempo real y no se guarda registro de los montos ingresados.

    **Descargo de Responsabilidad:**
    * Tu Resuelve Cambiario es una herramienta de referencia educativa y personal. No es una entidad financiera. 
    * Los valores del BCV se obtienen de su portal público. 
    * El usuario es el único responsable de sus decisiones de pago y negociaciones con terceros.
    * Los colaboradores de esta página no garantizan la precisión, exactitud, vigencia o disponibilidad continua de estos datos y se eximen de cualquier responsabilidad por errores u omisiones en la información mostrada, así como de interrupciones en el servicio.
        """)

st.caption("Desarrollado para análisis económico personal. Tu Resuelve Cambiario.")
