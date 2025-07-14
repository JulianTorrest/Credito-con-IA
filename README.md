# 🚗 Finanzauto: Tu Portal de Vehículos y Financiamiento con IA

![Finanzauto Logo](https://media.licdn.com/dms/image/v2/D4E0BAQG5TGatl4y1xA/company-logo_200_200/company-logo_200_200/0/1733493384307/finanzautocol_logo?e=2147483647&v=beta&t=Jsru4_8NEYo03Ca5nhxPCFDHCULciXr4NCi-5stILKk)

🌐 Despliegue en Streamlit Cloud (¡En Vivo!) 
La aplicación ya está desplegada y disponible públicamente en Streamlit Cloud. Puedes acceder a ella a través del siguiente enlace: https://credito-con-ia-julian.streamlit.app/

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

## 🏛️ Explicación de Decisiones Arquitectónicas y Stack Tecnológico

El diseño de Finanzauto se centra en la **rapidez de desarrollo**, la **interactividad de la interfaz de usuario** y la **potencia de la inteligencia artificial**, manteniendo a la vez la **simplicidad en el despliegue**.

* **Streamlit para la UI:** Elegido por su capacidad de construir aplicaciones web complejas y reactivas con puro Python, lo que acelera significativamente el ciclo de desarrollo y permite a los desarrolladores de IA e Ingenieros de Datos crear prototipos rápidamente sin necesidad de conocimientos profundos de desarrollo web frontend.
* **Google Gemini (Flash) como Core IA:** Se optó por los modelos Gemini de Google por su rendimiento robusto y su integración sencilla. Específicamente, el modelo `gemini-1.5-flash` fue seleccionado para todas las operaciones (embeddings y LLM para RAG y otras funcionalidades) debido a su **eficiencia en costos y alta velocidad de respuesta**, crucial para una experiencia de usuario fluida en una aplicación interactiva.
* **LangChain para Orquestación de LLM:** Este framework se utiliza para abstraer las complejidades de interactuar con los Modelos de Lenguaje Grandes y construir cadenas de procesamiento. Facilita la implementación de la Arquitectura RAG (Retrieval Augmented Generation), conectando los LLMs con la base de datos vectorial de manera eficiente y escalable.
* **ChromaDB como Base de Datos Vectorial:** Se eligió ChromaDB por su facilidad de uso, su capacidad de persistir datos localmente (lo que simplifica la gestión de la base de datos en entornos como Streamlit Cloud al no requerir un servidor de base de datos externo) y su excelente integración con LangChain para la gestión de embeddings y la búsqueda de similitud. La inclusión de `pysqlite3` es una medida preventiva para asegurar la compatibilidad con el entorno de ejecución de Streamlit Cloud.
* **Optimización de Rendimiento con Caching de Streamlit:** El uso de `@st.cache_resource` y `@st.cache_data` es una decisión arquitectónica clave para evitar recargar modelos costosos o recalcular datos intensivos en cada interacción del usuario, mejorando drásticamente la velocidad y eficiencia de la aplicación.
* **Gestión Segura de Credenciales:** La utilización de `st.secrets` para manejar la clave API de Google es una práctica de seguridad fundamental, asegurando que las credenciales sensibles no se expongan en el código fuente.
* **Modularidad del Código:** La aplicación está estructurada en funciones claras y modulares, lo que facilita la legibilidad, el mantenimiento y la futura expansión de nuevas características.

Esta combinación de herramientas permite que Finanzauto sea una solución potente, ágil y de fácil despliegue para el sector de financiamiento automotriz.

## 🚀 Cómo Empezar

Sigue estos pasos para configurar y ejecutar Finanzauto en tu máquina local:

### 1. Clona el Repositorio

```bash
git clone [https://github.com/JulianTorrest/Credito-con-IA.git](https://github.com/JulianTorrest/Credito-con-IA.git)
cd Credito-con-IA

### 2. Crea un Entorno Virtual (Recomendado)
python -m venv venv
# En Windows:
.\venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

### 3. Instala las Dependencias
pip install -r requirements.txt

streamlit
google-generativeai
langchain
langchain-google-genai
langchain-community
chromadb
PyMuPDF
pysqlite3


### 4. Configura tu Clave API de Google Gemini
# .streamlit/secrets.toml
GOOGLE_API_KEY="TU_CLAVE_API_DE_GEMINI_AQUI"

### 5. Ejecuta la Aplicación Streamlit
streamlit run main.py
La aplicación se abrirá automáticamente en tu navegador web (normalmente en http://localhost:8501).
