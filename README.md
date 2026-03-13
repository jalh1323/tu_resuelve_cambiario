# 💱 **Tu Resuelve Cambiario** 💱

Es una página web interactiva diseñada para ayudar a los venezolanos a tomar decisiones financieras rápidas al momento de realizar compras, comparando el pago en divisas (efectivo) frente al pago en bolívares.

## 🚀 Características
* **Tasas en Tiempo Real:** Obtiene la tasa oficial del BCV automáticamente.
* **Soporte de Fallback:** Si la API presenta fallas, el sistema permite el ingreso manual de la tasa para no interrumpir el uso.
* **Cálculo de Spread:** Muestra la brecha porcentual y nominal entre la tasa oficial y el mercado paralelo.
* **Decisión Inteligente:** Calcula el ahorro o pérdida en dólares y recomienda al usuario si le conviene más pagar en efectivo o vender sus divisas para pagar en bolívares.

## 🛠️ Tecnologías Usadas
* [Streamlit](https://streamlit.io/) - Framework para la interfaz web.
* [Requests](https://pypi.org/project/requests/) - Para el consumo de la API de tasas.
* [Python](https://www.python.org/)

## ⚙️ Uso Local
Si deseas correr este proyecto en tu propia computadora:

1. Clona este repositorio.
2. Instala las dependencias ejecutando: `pip install -r requirements.txt`
3. Inicia la aplicación con: `streamlit run tu_resuelve_cambiario.py` *(asegúrate de que tu archivo de código se llame tu_resuelve_cambiario.py)*.

## ⚖️ Aviso Legal y Privacidad
Esta aplicación es una herramienta de referencia educativa y personal. No recolecta, almacena ni comparte datos personales. Los desarrolladores no garantizan la exactitud o disponibilidad continua de los datos mostrados y se eximen de cualquier responsabilidad por decisiones financieras tomadas basadas en estos cálculos.
