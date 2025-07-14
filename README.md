# Credito-con-IA
# 🚗 Finanzauto: Tu Portal de Vehículos y Financiamiento con IA

![Finanzauto Logo/Banner](https://via.placeholder.com/1200x300/F0F2F6/000000?text=Finanzauto+AI+-+Cr%C3%A9dito+Vehicular+Inteligente)
*(Aquí puedes reemplazar la imagen con un banner real o el logo de tu aplicación)*

Finanzauto es una aplicación interactiva desarrollada con Streamlit y potenciada por la Inteligencia Artificial de Google Gemini, diseñada para revolucionar la experiencia de financiamiento automotriz. Ofrece un conjunto de herramientas inteligentes que asisten a los usuarios y asesores en el proceso de compra, venta, financiamiento y gestión de vehículos, desde la simulación de créditos hasta la valoración de autos usados y la asistencia en mantenimiento.

## ✨ Características Principales

* **Dashboard del Usuario:** Un resumen personalizado de la actividad del usuario, incluyendo el estado de sus solicitudes de crédito, vehículos favoritos y recomendaciones.
* **Simulador de Crédito:** Calcula pagos mensuales estimados basados en el monto del préstamo, plazo y tasa de interés.
* **Solicitud de Crédito:** Formulario para que los usuarios ingresen su información personal y financiera con fines de simulación y solicitud.
* **Análisis Preliminar con IA:** Utiliza el modelo Gemini para realizar un análisis inicial de elegibilidad crediticia basado en las reglas financieras.
* **Recomendador de Planes Financieros:** Asesora al usuario sobre planes de financiamiento ideales según su perfil financiero y prioridades.
* **Catálogo de Vehículos:** Explora una amplia selección de vehículos con filtros avanzados (marca, modelo, precio, tipo, combustible, año).
* **Comparador de Vehículos:** Permite comparar las características de dos vehículos lado a lado para una decisión informada.
* **Ingesta de Documentos (RAG):** Carga y procesa documentos (PDF, TXT, MD) para enriquecer la base de conocimiento del Asistente AI, utilizando ChromaDB como base de datos vectorial.
* **Asistente AI (RAG):** Un chatbot inteligente impulsado por Gemini que responde preguntas sobre los servicios de Finanzauto y el contenido de los documentos cargados.
* **Valoración de Vehículos Usados (IA):** Estima el precio de mercado de un vehículo usado basándose en sus características y el estado actual del mercado.
* **Asesor de Mantenimiento (IA):** Ofrece orientación sobre problemas comunes de vehículos, mantenimiento recomendado y costos de reparación.
* **Simulador de Escenarios Financieros (IA):** Analiza el impacto de diferentes situaciones (cambio de ingresos, deuda adicional, pagos extras) en un préstamo automotriz existente.
* **Calculadora de Impacto Ambiental:** Estima la huella de carbono y el costo anual de combustible/electricidad de diferentes tipos de vehículos.
* **Gamificación de Crédito:** Simula un sistema de puntos e insignias para motivar a los usuarios a completar hitos en su proceso de crédito.
* **Alertas de Vehículos:** Permite a los usuarios configurar notificaciones para cuando vehículos específicos estén disponibles.
* **Secciones Placeholder:** Incluye secciones conceptuales para un Portal de Clientes, Portal de Asesores, Blog y Soporte Multi-idioma, listas para futuras expansiones.

## 🛠️ Tecnologías Utilizadas

* **Python:** Lenguaje de programación principal.
* **Streamlit:** Framework para construir la interfaz de usuario de la aplicación web.
* **Google Gemini API:** Para todas las capacidades de Inteligencia Artificial (modelos de embeddings y modelos de lenguaje).
* **LangChain:** Framework para construir aplicaciones impulsadas por modelos de lenguaje, facilitando la integración de RAG.
* **ChromaDB:** Base de datos vectorial persistente para almacenar y buscar embeddings de documentos.
* **PyMuPDF (fitz):** Para la extracción de texto de documentos PDF.
* **pysqlite3:** Para asegurar la compatibilidad de SQLite con ChromaDB en entornos como Streamlit Cloud.

## 🚀 Cómo Empezar

Sigue estos pasos para configurar y ejecutar Finanzauto en tu máquina local:

### 1. Clona el Repositorio

```bash
git clone [https://github.com/JulianTorrest/Credito-con-IA.git](https://github.com/JulianTorrest/Credito-con-IA.git)
cd Credito-con-IA

2. Crea un Entorno Virtual (Recomendado)
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

3. Instala las Dependencias
pip install -r requirements.txt

streamlit
google-generativeai
langchain
langchain-google-genai
langchain-community
chromadb
PyMuPDF
pysqlite3


4. Configura tu Clave API de Google Gemini
# .streamlit/secrets.toml
GOOGLE_API_KEY="TU_CLAVE_API_DE_GEMINI_AQUI"

5. Ejecuta la Aplicación Streamlit
streamlit run main.py
