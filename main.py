import os
import streamlit as st
import google.generativeai as genai

# Ya no necesitamos 'from dotenv import load_dotenv' ni 'load_dotenv()'
# cuando estamos en Streamlit Cloud y usando sus Secrets.

# --- Configuración de la API de Gemini ---
# La clave API se debe configurar en los 'Secrets' de tu app en Streamlit Cloud
# bajo el nombre 'GOOGLE_API_KEY'.
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except KeyError:
    st.error("⚠️ Error: La clave API de Gemini ('GOOGLE_API_KEY') no está configurada en los Secrets de Streamlit Cloud.")
    st.info("Por favor, ve a la configuración de tu app en Streamlit Cloud > Secrets y añade GOOGLE_API_KEY='tu_clave_aqui'")
    st.stop() # Detiene la ejecución de la aplicación si la clave no se encuentra.

genai.configure(api_key=GOOGLE_API_KEY)

# --- El resto de tus imports y código ---
import random
import math
from datetime import datetime, timedelta
import fitz # PyMuPDF for PDF processing
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import sys

# Estas líneas son cruciales para el problema de sqlite3 con ChromaDB
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


# Initialize the generative model with Gemini 1.5 Flash
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    # Initialize the embeddings model
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
except Exception as e:
    st.error(f"❌ **Error al cargar el modelo Gemini o embeddings:** {e}")
    st.info("Asegúrate de que 'gemini-1.5-flash' y 'models/embedding-001' estén disponibles y que tu clave API sea correcta.")
    st.stop() # Stop execution if models cannot be loaded

# --- ChromaDB Setup ---
CHROMA_DB_DIR = "chroma_db" # Directorio para almacenar la base de datos vectorial

@st.cache_resource
def get_vector_store():
    """Initializes and returns the ChromaDB vector store."""
    try:
        # Attempt to load an existing ChromaDB instance
        vector_store = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings_model)
        st.success(f"Cargada base de datos vectorial existente de '{CHROMA_DB_DIR}'. Documentos cargados: {vector_store._collection.count()}")
    except Exception:
        # If loading fails (e.g., directory doesn't exist or is empty), create a new one
        vector_store = Chroma.from_texts(texts=[], embedding=embeddings_model, persist_directory=CHROMA_DB_DIR)
        st.info(f"Creada nueva base de datos vectorial en '{CHROMA_DB_DIR}'.")
    return vector_store

vector_store = get_vector_store()

# --- Dummy Data Generation (Dynamic) ---
@st.cache_data
def generate_random_vehicles(num_vehicles=5000):
    makes = ["Toyota", "Honda", "Ford", "Chevrolet", "BMW", "Mercedes-Benz", "Audi", "Tesla", "Hyundai", "Kia", "Nissan", "Mazda", "Subaru", "Volvo", "Volkswagen"]
    models_by_make = {
        "Toyota": ["Corolla", "Camry", "RAV4", "Highlander", "Tacoma", "Sienna", "Prius"],
        "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Ridgeline", "Odyssey", "HR-V"],
        "Ford": ["F-150", "Explorer", "Escape", "Mustang", "Bronco", "Ranger", "Maverick"],
        "Chevrolet": ["Silverado", "Equinox", "Traverse", "Malibu", "Camaro", "Tahoe", "Blazer"],
        "BMW": ["3 Series", "5 Series", "X1", "X3", "X5", "X7", "iX"],
        "Mercedes-Benz": ["C-Class", "E-Class", "GLC", "GLE", "S-Class", "EQE", "EQS"],
        "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7", "e-tron"],
        "Tesla": ["Model 3", "Model Y", "Model S", "Model X", "Cybertruck"],
        "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe", "Kona", "Palisade", "Ioniq 5"],
        "Kia": ["Forte", "K5", "Sportage", "Sorento", "Telluride", "Niro", "EV6"],
        "Nissan": ["Altima", "Sentra", "Rogue", "Titan", "Murano", "Pathfinder", "Frontier"],
        "Mazda": ["Mazda3", "Mazda6", "CX-5", "CX-9", "MX-5 Miata"],
        "Subaru": ["Impreza", "Legacy", "Forester", "Outback", "Crosstrek", "Ascent"],
        "Volvo": ["S60", "S90", "XC40", "XC60", "XC90", "C40 Recharge"],
        "Volkswagen": ["Jetta", "Passat", "Tiguan", "Atlas", "GTI", "ID.4"]
    }
    vehicle_types = ["Sedan", "SUV", "Truck", "Hatchback", "Coupe", "Convertible", "Minivan", "EV"]
    fuel_types = ["Gasoline", "Hybrid", "Electric", "Diesel"]
    common_features = [
        "Bluetooth", "Backup Camera", "Sunroof", "Leather Seats", "Navigation System",
        "Heated Seats", "Lane Assist", "Adaptive Cruise Control", "AWD", "Keyless Entry",
        "Apple CarPlay", "Android Auto", "Blind Spot Monitoring", "Towing Package",
        "Premium Sound System", "Panoramic Roof", "Automatic Emergency Braking"
    ]

    vehicles = []
    for i in range(1, num_vehicles + 1):
        make = random.choice(makes)
        model = random.choice(models_by_make.get(make, ["Generic Model"]))
        year = random.randint(2018, 2025)
        
        base_price = random.randint(15000, 80000)
        if "BMW" in make or "Mercedes-Benz" in make or "Audi" in make or "Tesla" in make:
            base_price = random.randint(35000, 120000)
        price = base_price + (year - 2018) * random.uniform(500, 2000) + random.uniform(-1000, 1000)
        price = max(10000, price)
        
        v_type = random.choice(vehicle_types)
        fuel = random.choice(fuel_types)
        
        if v_type == "EV":
            fuel = "Electric"
            price = random.randint(35000, 90000)

        num_features = random.randint(2, 6)
        selected_features = random.sample(common_features, num_features)

        vehicles.append({
            "id": i,
            "make": make,
            "model": model,
            "year": year,
            "price": round(price, 2),
            "type": v_type,
            "fuel": fuel,
            "features": selected_features,
            "mileage": random.randint(500, 150000) if year < 2025 else random.randint(10, 5000),
            "color": random.choice(["White", "Black", "Silver", "Red", "Blue", "Gray", "Green", "Yellow"])
        })
    return vehicles

DUMMY_VEHICLES = generate_random_vehicles(num_vehicles=5000)

# --- Simulate User Data for Dashboard (for a single dummy user) ---
if 'dummy_user_data' not in st.session_state or 'loan_applications' not in st.session_state.dummy_user_data:
    st.session_state.dummy_user_data = {
        "name": "Juan Pérez",
        "email": "juan.perez@example.com",
        "loan_applications": [
            {"id": "APP001", "vehicle": "Toyota RAV4 2023", "amount": 32000, "status": "Aprobada", "stage": "Desembolsado", "date": "2025-06-01"},
            {"id": "APP002", "vehicle": "Ford F-150 2022", "amount": 45000, "status": "En Revisión", "stage": "Análisis Preliminar", "date": "2025-07-10"},
            {"id": "APP003", "vehicle": "Tesla Model 3 2024", "amount": 40000, "status": "Rechazada", "stage": "Análisis Preliminar", "date": "2025-05-15", "reason": "Ingresos insuficientes"},
            {"id": "APP004", "vehicle": "Honda Civic 2024", "amount": 28000, "status": "En Revisión", "stage": "Recopilación de Documentos", "date": "2025-07-05"},
            {"id": "APP005", "vehicle": "BMW X5 2023", "amount": 60000, "status": "Aprobada", "stage": "Firma de Contrato", "date": "2025-07-12"}
        ],
        "favorite_vehicles": random.sample(DUMMY_VEHICLES, k=3),
        "recommended_vehicles": random.sample(DUMMY_VEHICLES, k=2)
    }

# --- Streamlit App Structure ---
st.set_page_config(layout="wide", page_title="Finanzauto", initial_sidebar_state="expanded")

st.title("🚗 Finanzauto: Tu Portal de Vehículos y Financiamiento")

# --- Temporary Reset for Development ---
if st.sidebar.button("Reiniciar Datos de la App (Desarrollo)"):
    st.session_state.clear()
    st.cache_data.clear()
    
    # Also clear ChromaDB directory for a full reset
    if os.path.exists(CHROMA_DB_DIR):
        import shutil
        shutil.rmtree(CHROMA_DB_DIR)
        st.warning(f"Directorio ChromaDB '{CHROMA_DB_DIR}' borrado.")
    
    st.rerun()

# --- Sidebar Navigation (Main Menu) ---
st.sidebar.header("Menú Principal")
pages = {
    "Dashboard": "📊 Dashboard del Usuario",
    "Simulador de Crédito": "💰 Simulador de Crédito",
    "Solicitud de Crédito": "📝 Solicitud de Crédito",
    "Análisis Preliminar": "🔎 Análisis Preliminar",
    "Recomendador de Planes": "💡 Recomendador de Planes",
    "Catálogo de Vehículos": "🚗 Catálogo de Vehículos",
    "Comparador": "⚖️ Comparador de Vehículos",
    "Ingesta de Documentos (RAG)": "📂 Ingesta de Documentos para RAG", # NEW PAGE
    "Asistente AI (RAG)": "🤖 Asistente AI", # Modified for RAG
    "Valoración de Vehículos Usados (IA)": "📈 Valoración de Vehículos Usados (IA)",
    "Asesor de Mantenimiento (IA)": "🔧 Asesor de Mantenimiento (IA)",
    "Simulador de Escenarios Financieros (IA)": "🔮 Simulador de Escenarios Financieros (IA)",
    "Calculadora de Impacto Ambiental": "🌎 Calculadora de Impacto Ambiental",
    "Gamificación de Crédito": "🎮 Gamificación de Crédito",
    "Alertas de Vehículos": "🔔 Alertas de Vehículos",
    "Portal de Clientes": "👤 Portal de Clientes",
    "Portal de Asesores": "💼 Portal de Asesores",
    "Blog": "📰 Blog",
    "Soporte Multi-idioma": "🌐 Soporte Multi-idioma",
}

selected_page = st.sidebar.radio("Navegación", list(pages.keys()))

# --- Page Content ---
st.header(pages[selected_page])

if selected_page == "Dashboard":
    st.info("¡Bienvenido, Juan Pérez! Aquí tienes un resumen de tu actividad en Finanzauto.")

    user_data = st.session_state.dummy_user_data

    tab_titles = ["Todas las Solicitudes", "En Análisis/Revisión", "Documentos Pendientes", "Aprobadas", "Firmado/Desembolsado", "Rechazadas"]
    tabs = st.tabs(tab_titles)

    applications_by_stage = {
        "Todas las Solicitudes": user_data["loan_applications"],
        "En Análisis/Revisión": [app for app in user_data["loan_applications"] if app.get("stage") == "Análisis Preliminar" or app.get("status") == "En Revisión"],
        "Documentos Pendientes": [app for app in user_data["loan_applications"] if app.get("stage") == "Recopilación de Documentos"],
        "Aprobadas": [app for app in user_data["loan_applications"] if app.get("status") == "Aprobada"],
        "Firmado/Desembolsado": [app for app in user_data["loan_applications"] if app.get("stage") == "Firma de Contrato" or app.get("stage") == "Desembolsado"],
        "Rechazadas": [app for app in user_data["loan_applications"] if app.get("status") == "Rechazada"]
    }

    for i, tab_title in enumerate(tab_titles):
        with tabs[i]:
            st.subheader(f"Solicitudes: {tab_title}")
            current_apps = applications_by_stage[tab_title]
            if current_apps:
                for app in current_apps:
                    status_emoji = "✅" if app.get("status") == "Aprobada" else "⏳" if app.get("status") == "En Revisión" else "❌"
                    st.markdown(f"- **Solicitud {app.get('id', 'N/A')}:** Vehículo: {app.get('vehicle', 'N/A')} | Monto: ${app.get('amount', 0):,.2f} | Estado: **{status_emoji} {app.get('status', 'Desconocido')}** | Etapa: _{app.get('stage', 'Desconocida')}_ ({app.get('date', 'N/A')})")
                    if "reason" in app:
                        st.info(f"    *Razón:* {app['reason']}")
                st.markdown("---")
            else:
                st.write(f"No hay solicitudes en la etapa '{tab_title}' en este momento.")

    st.subheader("Tus Vehículos Favoritos")
    if user_data["favorite_vehicles"]:
        for fav_car in user_data["favorite_vehicles"]:
            st.markdown(f"- **{fav_car['year']} {fav_car['make']} {fav_car['model']}** (Precio: ${fav_car['price']:,.2f})")
            st.markdown(f"  *Tipo: {fav_car['type']}, Combustible: {fav_car['fuel']}*")
        st.markdown("---")
    else:
        st.write("Aún no has marcado ningún vehículo como favorito.")

    st.subheader("Recomendaciones de Vehículos para Ti")
    st.write("Basado en tus intereses y actividad, estas son algunas recomendaciones:")
    if user_data["recommended_vehicles"]:
        for rec_car in user_data["recommended_vehicles"]:
            st.markdown(f"- **{rec_car['year']} {rec_car['make']} {rec_car['model']}** (Precio: ${rec_car['price']:,.2f})")
            st.markdown(f"  *Ideal para: [Explicación generada por IA en la sección de Recomendador de Planes]*")
        st.markdown("---")
    else:
        st.write("No hay recomendaciones personalizadas en este momento. Explora el catálogo o usa el recomendador.")

elif selected_page == "Simulador de Crédito":
    st.write("Calcula tus pagos estimados.")
    
    loan_amount = st.slider("Monto del Préstamo ($)", 5000, 100000, 30000, step=1000)
    loan_term_years = st.slider("Plazo (años)", 1, 7, 5)
    interest_rate = st.slider("Tasa de Interés Anual (%)", 2.0, 15.0, 7.5, step=0.1)

    if st.button("Calcular"):
        monthly_rate = (interest_rate / 100) / 12
        num_payments = loan_term_years * 12
        if monthly_rate > 0:
            monthly_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate)**-num_payments)
        else:
            monthly_payment = loan_amount / num_payments

        total_payment = monthly_payment * num_payments
        total_interest = total_payment - loan_amount

        st.subheader("Resultados del Cálculo:")
        st.write(f"**Monto del Préstamo:** ${loan_amount:,.2f}")
        st.write(f"**Plazo:** {loan_term_years} años ({num_payments} meses)")
        st.write(f"**Tasa de Interés Anual:** {interest_rate:.1f}%")
        st.markdown(f"---")
        st.success(f"**Pago Mensual Estimado:** ${monthly_payment:,.2f}")
        st.info(f"**Pago Total Estimado:** ${total_payment:,.2f}")
        st.info(f"**Intereses Totales Estimados:** ${total_interest:,.2f}")

elif selected_page == "Solicitud de Crédito":
    st.info("Por favor, rellena tus datos para solicitar un crédito automotriz.")
    with st.form("credit_application_form"):
        st.subheader("Información Personal")
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("Nombre(s)", key="app_first_name")
            email = st.text_input("Correo Electrónico", key="app_email")
        with col2:
            last_name = st.text_input("Apellido(s)", key="app_last_name")
            phone = st.text_input("Teléfono", key="app_phone")

        st.subheader("Información Financiera")
        st.session_state.income = st.number_input("Ingresos Mensuales Netos ($)", min_value=0, value=2000, key="app_income")
        st.session_state.existing_debts = st.number_input("Deudas Mensuales Existentes ($)", min_value=0, value=500, key="app_existing_debts")
        st.session_state.desired_vehicle_price = st.number_input("Precio del Vehículo Deseado ($)", min_value=0, value=30000, key="app_desired_vehicle_price")
        
        # New inputs for Personalización de Tasas
        st.subheader("Información Adicional (para Personalización de Tasas)")
        job_stability = st.selectbox("Estabilidad Laboral", ["Empleado Fijo", "Contratista", "Independiente", "Desempleado"], key="app_job_stability")
        vehicle_type_interest = st.selectbox("Tipo de Vehículo de Interés", ["Sedan", "SUV", "Camioneta", "Deportivo", "Eléctrico"], key="app_vehicle_type_interest")

        submitted = st.form_submit_button("Enviar Solicitud")
        if submitted:
            if not first_name or not last_name or not email:
                st.warning("Por favor, completa todos los campos obligatorios.")
            else:
                st.success(f"Solicitud recibida para {first_name} {last_name}. Un asesor se pondrá en contacto pronto.")
                st.json({
                    "nombre": first_name,
                    "apellido": last_name,
                    "email": email,
                    "telefono": phone,
                    "ingresos": st.session_state.income,
                    "deudas_existentes": st.session_debts,
                    "precio_vehiculo_deseado": st.session_state.desired_vehicle_price,
                    "estabilidad_laboral": job_stability,
                    "tipo_vehiculo_interes": vehicle_type_interest
                })

elif selected_page == "Análisis Preliminar":
    st.info("Aquí se mostrará un análisis automatizado inicial de tu elegibilidad, basado en la información que proporciones en la sección de 'Solicitud de Crédito'.")

    income = st.session_state.get('income', 0)
    existing_debts = st.session_state.get('existing_debts', 0)
    desired_vehicle_price = st.session_state.get('desired_vehicle_price', 0)

    if income == 0 and existing_debts == 0 and desired_vehicle_price == 0:
        st.warning("Por favor, completa la 'Solicitud de Crédito' para obtener un análisis preliminar.")
    else:
        st.subheader("Tus Datos de Solicitud (para el análisis):")
        st.write(f"- Ingresos Mensuales Netos: ${income:,.2f}")
        st.write(f"- Deudas Mensuales Existentes: ${existing_debts:,.2f}")
        st.write(f"- Precio del Vehículo Deseado: ${desired_vehicle_price:,.2f}")

        if st.button("Realizar Análisis Preliminar con IA"):
            with st.spinner("Analizando tus datos con IA..."):
                try:
                    credit_rules_prompt = """
                    Reglas de elegibilidad generales para un préstamo automotriz:
                    1. La relación Ingresos/Deudas (DTI) después de la posible cuota del vehículo idealmente no debe exceder el 40% del ingreso neto.
                    2. Un buen indicador de capacidad de pago es que el ingreso neto sea al menos 3 veces el pago mensual estimado.
                    3. El precio del vehículo deseado no debe ser excesivamente alto en comparación con los ingresos (e.g., no más de 3 veces el ingreso anual).
                    4. Se valora un ingreso neto superior a $1,500 USD mensuales.
                    5. El total de deudas (existentes + pago estimado del vehículo) no debe superar el 60% del ingreso neto.
                    """

                    estimated_monthly_payment = (desired_vehicle_price * 0.08 / 12) / (1 - (1 + 0.08 / 12)**-(60)) # 8% annual, 60 months

                    # Detección de Fraude (IA) - placeholder
                    fraud_detection_result = "No se detectaron anomalías significativas (simulado)."
                    if random.random() < 0.05: # 5% chance of simulated fraud
                        fraud_detection_result = "Anomalía detectada: Posible inconsistencia en la relación ingresos/precio del vehículo. Requiere revisión manual."

                    prompt_for_gemini = f"""
                    Eres un analista de crédito de Finanzauto. Necesito tu análisis preliminar de la elegibilidad de un cliente para un préstamo automotriz.
                    Aquí están los datos del cliente:
                    - Ingresos Mensuales Netos: ${income:,.2f}
                    - Deudas Mensuales Existentes (excluyendo el posible préstamo del auto): ${existing_debts:,.2f}
                    - Precio del Vehículo Deseado: ${desired_vehicle_price:,.2f}
                    - Pago mensual estimado del vehículo deseado (basado en un cálculo promedio): ${estimated_monthly_payment:,.2f}

                    {credit_rules_prompt}

                    Basado en estos datos y las reglas generales, por favor, proporciona un análisis preliminar conciso.
                    Clasifica la elegibilidad en una de estas categorías: "Altamente Probable", "Requiere Revisión Adicional", "Poco Probable".
                    Explica brevemente las razones de tu clasificación y sugiere qué pasos podría tomar el cliente si la elegibilidad no es "Altamente Probable".
                    Además, incluye un apartado de 'Detección de Fraude (IA)' con el siguiente resultado: "{fraud_detection_result}".
                    """
                    
                    response = model.generate_content(prompt_for_gemini)
                    ai_analysis = response.text
                    st.session_state["ai_preliminary_analysis_output"] = ai_analysis # Store for gamification

                    st.subheader("Resultados del Análisis Preliminar de IA:")
                    st.markdown(ai_analysis)

                except Exception as e:
                    st.error(f"Lo siento, hubo un error al realizar el análisis. Por favor, inténtalo de nuevo. Error: {e}")

elif selected_page == "Recomendador de Planes":
    st.info("Cuéntanos sobre tus necesidades y te ayudaremos a encontrar el plan de financiamiento ideal.")

    with st.form("financial_plan_recommender_form"):
        st.subheader("Tus Datos Financieros y Preferencias")
        
        col_form1, col_form2 = st.columns(2)
        with col_form1:
            vehicle_value = st.number_input("Valor del Vehículo Deseado ($)", min_value=10000, value=50000, step=1000, key="reco_vehicle_value")
            initial_payment = st.number_input("Cuota Inicial ($)", min_value=0, value=10000, step=500, key="reco_initial_payment")
            monthly_income = st.number_input("Ingresos Mensuales Netos ($)", min_value=500, value=3000, step=100, key="reco_monthly_income")
        with col_form2:
            monthly_expenses = st.number_input("Gastos Mensuales (sin auto) ($)", min_value=0, value=1000, step=50, key="reco_monthly_expenses")
            credit_history = st.selectbox(
                "Historial de Crédito",
                options=["Excelente", "Bueno", "Regular", "Limitado/Sin historial"],
                key="reco_credit_history"
            )
            priority = st.selectbox(
                "¿Qué priorizas en tu crédito?",
                options=["Cuota mensual baja", "Pagar el préstamo rápidamente", "Flexibilidad en pagos/refinanciamiento", "Bajas tasas de interés"],
                key="reco_priority"
            )
            # Input para personalización de tasas
            job_stability_reco = st.selectbox("Estabilidad Laboral (para personalización)", ["Empleado Fijo", "Contratista", "Independiente", "Desempleado"], key="reco_job_stability")
            vehicle_type_interest_reco = st.selectbox("Tipo de Vehículo de Interés (para personalización)", ["Sedan", "SUV", "Camioneta", "Deportivo", "Eléctrico"], key="reco_vehicle_type_interest")

        submitted_reco = st.form_submit_button("Encontrar mi Plan Ideal")

        if submitted_reco:
            if vehicle_value <= initial_payment:
                st.error("El valor del vehículo debe ser mayor que la cuota inicial.")
            elif monthly_income <= monthly_expenses:
                st.error("Tus ingresos mensuales deben ser mayores que tus gastos mensuales para calificar.")
            else:
                with st.spinner("Analizando tus datos y encontrando planes ideales..."):
                    loan_amount = vehicle_value - initial_payment
                    disposable_income = monthly_income - monthly_expenses
                    
                    # Dummy plans and their characteristics (simplified for prompt)
                    # In a real app, these would come from a database/system
                    dummy_loan_plans_data = [
                        {"name": "Plan Balance Ideal", "description": "Este plan está diseñado para un pago mensual equilibrado, ajustándose a tus ingresos y gastos, mientras mantiene la deuda manejable. Es la opción más sensata considerando tu preferencia por un balance.", "min_term": 48, "max_term": 72, "base_rate": 0.22, "priority_match": ["Cuota mensual baja", "Flexibilidad en pagos/refinanciamiento"], "income_factor": 0.35}, # 22% E.A.
                        {"name": "Plan Pago Rápido", "description": "Si tu objetivo es reducir la deuda y minimizar los intereses totales, este plan te permite pagar más rápido con cuotas más altas pero un plazo menor.", "min_term": 24, "max_term": 48, "base_rate": 0.20, "priority_match": ["Pagar el préstamo rápidamente", "Bajas tasas de interés"], "income_factor": 0.45}, # 20% E.A.
                        {"name": "Plan Flexi-Cuota", "description": "Con plazos extendidos y la opción de pagos extraordinarios, este plan ofrece máxima flexibilidad para adaptarse a cambios en tu situación financiera.", "min_term": 60, "max_term": 84, "base_rate": 0.25, "priority_match": ["Flexibilidad en pagos/refinanciamiento", "Cuota mensual baja"], "income_factor": 0.30}, # 25% E.A.
                    ]

                    generated_plans_info = []

                    for plan_template in dummy_loan_plans_data:
                        # Adjust rate based on credit history and new factors (Personalización de Tasas - IA)
                        adjusted_rate = plan_template["base_rate"]
                        if credit_history == "Excelente":
                            adjusted_rate -= 0.02
                        elif credit_history == "Bueno":
                            adjusted_rate -= 0.01
                        elif credit_history == "Limitado/Sin historial":
                            adjusted_rate += 0.03
                        
                        # Apply new factors for advanced personalization (dummy logic)
                        if job_stability_reco == "Empleado Fijo":
                            adjusted_rate -= 0.005
                        elif job_stability_reco == "Independiente":
                            adjusted_rate += 0.01

                        if vehicle_type_interest_reco == "Eléctrico":
                            adjusted_rate -= 0.005 # Incentive for EVs

                        adjusted_rate = max(0.18, adjusted_rate) # Minimum rate

                        # Calculate term based on priority and disposable income
                        calculated_term_months = 60 # Default for Balance Ideal

                        if plan_template["name"] == "Plan Pago Rápido":
                            # Try to find a term where payment is a higher percentage of income
                            target_payment_ratio = 0.35 # Aim for 35% of disposable income
                            target_payment = disposable_income * target_payment_ratio
                            
                            # Add a check for target_payment to avoid division by zero or negative log argument
                            if target_payment <= 0:
                                calculated_term_months = plan_template["max_term"] # Fallback to max term if target payment is too low/zero
                            else:
                                monthly_rate = adjusted_rate / 12
                                if monthly_rate > 0:
                                    # Ensure the argument for log is positive
                                    log_arg = 1 - (monthly_rate * loan_amount) / target_payment
                                    if log_arg <= 0:
                                        calculated_term_months = plan_template["max_term"]
                                    else:
                                        term_calc = -math.log(log_arg) / math.log(1 + monthly_rate)
                                        calculated_term_months = round(term_calc)
                                else:
                                    calculated_term_months = round(loan_amount / target_payment) if target_payment > 0 else plan_template["max_term"]

                            calculated_term_months = max(plan_template["min_term"], min(plan_template["max_term"], calculated_term_months))
                            
                        elif plan_template["name"] == "Plan Flexi-Cuota":
                            # Try to find a term where payment is a lower percentage of income
                            target_payment_ratio = 0.25 # Aim for 25% of disposable income
                            target_payment = disposable_income * target_payment_ratio

                            # Add a check for target_payment to avoid division by zero or negative log argument
                            if target_payment <= 0:
                                calculated_term_months = plan_template["max_term"]
                            else:
                                monthly_rate = adjusted_rate / 12
                                if monthly_rate > 0:
                                    # Ensure the argument for log is positive
                                    log_arg = 1 - (monthly_rate * loan_amount) / target_payment
                                    if log_arg <= 0:
                                        calculated_term_months = plan_template["max_term"]
                                    else:
                                        term_calc = -math.log(log_arg) / math.log(1 + monthly_rate)
                                        calculated_term_months = round(term_calc)
                                else:
                                    calculated_term_months = round(loan_amount / target_payment) if target_payment > 0 else plan_template["max_term"]
                                    
                            calculated_term_months = max(plan_template["min_term"], min(plan_template["max_term"], calculated_term_months))
                        
                        # Fallback for balance or if calculated term is out of range
                        if not (plan_template["min_term"] <= calculated_term_months <= plan_template["max_term"]):
                            calculated_term_months = random.randint(plan_template["min_term"], plan_template["max_term"])

                        monthly_rate = adjusted_rate / 12
                        if monthly_rate > 0 and calculated_term_months > 0:
                            denominator = (1 - (1 + monthly_rate)**-calculated_term_months)
                            if denominator == 0:
                                monthly_payment = loan_amount / calculated_term_months
                            else:
                                monthly_payment = (loan_amount * monthly_rate) / denominator
                        else:
                            monthly_payment = loan_amount / calculated_term_months if calculated_term_months > 0 else 0

                        total_payment = monthly_payment * calculated_term_months
                        total_interest = total_payment - loan_amount

                        generated_plans_info.append({
                            "name": plan_template["name"],
                            "description": plan_template["description"],
                            "cuota_mensual": monthly_payment,
                            "plazo_meses": calculated_term_months,
                            "tasa_anual": adjusted_rate * 100,
                            "monto_financiado": loan_amount,
                            "intereses_totales": total_interest,
                            "advantages": [],
                            "disadvantages": []
                        })
                    
                    plans_for_ai_prompt = ""
                    for i, plan in enumerate(generated_plans_info):
                        plans_for_ai_prompt += f"Plan {i+1}:\n"
                        plans_for_ai_prompt += f"  Nombre: {plan['name']}\n"
                        plans_for_ai_prompt += f"  Descripción: {plan['description']}\n"
                        plans_for_ai_prompt += f"  Cuota Mensual Estimada: ${plan['cuota_mensual']:,.2f}\n"
                        plans_for_ai_prompt += f"  Plazo: {plan['plazo_meses']} meses\n"
                        plans_for_ai_prompt += f"  Tasa Anual: {plan['tasa_anual']:.2f}% E.A.\n"
                        plans_for_ai_prompt += f"  Monto Financiado: ${plan['monto_financiado']:,.2f}\n"
                        plans_for_ai_prompt += f"  Intereses Totales: ${plan['intereses_totales']:,.2f}\n\n"

                    ai_prompt = f"""
                    Como experto financiero de Finanzauto, te proporciono los datos de un cliente y tres posibles planes de financiamiento.
                    Tu tarea es:
                    1. Reafirmar cuál de los planes es el **más adecuado** basado en la prioridad del cliente.
                    2. Para cada plan, genera una sección de "Ventajas" y "Desventajas" específicas, considerando los datos del cliente y el plan.
                    3. La descripción inicial de cada plan ya está provista, pero puedes complementarla si lo consideras necesario.

                    Datos del Cliente:
                    - Valor del Vehículo Deseado: ${vehicle_value:,.2f}
                    - Cuota Inicial: ${initial_payment:,.2f}
                    - Monto a Financiar: ${loan_amount:,.2f}
                    - Ingresos Mensuales Netos: ${monthly_income:,.2f}
                    - Gastos Mensuales (sin auto): ${monthly_expenses:,.2f}
                    - Ingreso Disponible (para pago de deuda): ${disposable_income:,.2f}
                    - Historial de Crédito: {credit_history}
                    - Prioridad en el Crédito: "{priority}"
                    - Estabilidad Laboral: {job_stability_reco}
                    - Tipo de Vehículo de Interés: {vehicle_type_interest_reco}

                    Planes de Financiamiento Calculados (pre-calculados):
                    {plans_for_ai_prompt}

                    Genera la salida estructurada como una lista de tarjetas. Cada tarjeta debe seguir exactamente este formato Markdown, incluyendo los saltos de línea y el formato negrita/itálica.
                    Asegúrate de que los valores numéricos estén formateados con puntos para miles y comas para decimales, y el símbolo de dólar ($) al inicio, como "$ 1.145.775".

                    ---
                    **[Nombre del Plan]**
                    [Descripción del plan, puede ser la proporcionada o ligeramente mejorada por la IA]
                    **Cuota Mensual Estimada**
                    $[Cuota Mensual del Plan, formateada]
                    **Plazo**
                    [Plazo en meses] meses
                    **Tasa Anual**
                    [Tasa anual formateada]% E.A.
                    **Monto Financiado**
                    $[Monto Financiado formateado]
                    **Intereses Totales**
                    $[Intereses Totales formateado]

                    **Ventajas**
                    * [Ventaja 1 específica del plan y del cliente]
                    * [Ventaja 2 específica del plan y del cliente]
                    * [Ventaja 3 específica del plan y del cliente]

                    **Desventajas**
                    * [Desventaja 1 específica del plan y del cliente]
                    * [Desventaja 2 específica del plan y del cliente]
                    * [Desventaja 3 específica del plan y del cliente]
                    ---

                    Asegúrate de generar 3 tarjetas, una por cada plan proporcionado en la entrada, y que la "Descripción" de cada plan sea adecuada y coherente con el nombre y la filosofía del plan.
                    """

                    try:
                        response = model.generate_content(ai_prompt)
                        ai_recommendations_markdown = response.text
                        st.session_state["recommended_plans_output"] = ai_recommendations_markdown
                        
                    except Exception as e:
                        st.error(f"Lo siento, hubo un error al generar las recomendaciones de planes. Por favor, inténtalo de nuevo. Error: {e}")
                        st.session_state["recommended_plans_output"] = None
        
    if "recommended_plans_output" in st.session_state and st.session_state["recommended_plans_output"]:
        st.subheader("Planes de Financiamiento Recomendados")
        # Split the markdown by the "---" separator to get individual cards
        raw_cards = st.session_state["recommended_plans_output"].split("---")
        # Filter out empty strings from splitting and strip whitespace
        processed_cards = [card.strip() for card in raw_cards if card.strip()]
        
        if processed_cards:
            for i, card_content in enumerate(processed_cards):
                st.markdown(card_content)
                st.button(f"Seleccionar este Plan (Plan {i+1})", key=f"select_plan_{i}")
                st.markdown("---")
        else:
            st.warning("No se pudieron generar recomendaciones de planes. Por favor, ajusta tus datos.")

elif selected_page == "Catálogo de Vehículos":
    st.info(f"Explora nuestra selección de {len(DUMMY_VEHICLES):,} vehículos disponibles.")

    st.subheader("Filtros y Búsqueda")
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        search_query = st.text_input("Buscar por Marca o Modelo", "", key="catalog_search_query").lower()
        min_price = st.number_input("Precio Mínimo ($)", min_value=0, value=0, step=1000, key="catalog_min_price")
    with col_filter2:
        max_price = st.number_input("Precio Máximo ($)", min_value=0, value=150000, step=1000, key="catalog_max_price")
        selected_types = st.multiselect("Tipo de Vehículo", options=sorted(list(set([v['type'] for v in DUMMY_VEHICLES]))), key="catalog_types")
    with col_filter3:
        selected_fuels = st.multiselect("Tipo de Combustible", options=sorted(list(set([v['fuel'] for v in DUMMY_VEHICLES]))), key="catalog_fuels")
        selected_year = st.slider("Año Mínimo", min_value=2018, max_value=2025, value=2018, key="catalog_year")

    st.markdown("---")

    filtered_vehicles = []
    for vehicle in DUMMY_VEHICLES:
        match = True
        if search_query:
            if search_query not in vehicle['make'].lower() and \
               search_query not in vehicle['model'].lower():
                match = False
        if not (min_price <= vehicle['price'] <= max_price):
            match = False
        if selected_types and vehicle['type'] not in selected_types:
            match = False
        if selected_fuels and vehicle['fuel'] not in selected_fuels:
            match = False
        if vehicle['year'] < selected_year:
            match = False

        if match:
            filtered_vehicles.append(vehicle)
    
    st.write(f"Mostrando **{len(filtered_vehicles):,}** de **{len(DUMMY_VEHICLES):,}** vehículos que cumplen los criterios.")

    display_limit = 200
    if filtered_vehicles:
        for vehicle in filtered_vehicles[:display_limit]:
            st.subheader(f"{vehicle['year']} {vehicle['make']} {vehicle['model']}")
            st.write(f"**Tipo:** {vehicle['type']} | **Combustible:** {vehicle['fuel']} | **Kilometraje:** {vehicle['mileage']:,} km")
            st.write(f"**Color:** {vehicle['color']} | **Características:** {', '.join(vehicle['features'])}")
            st.markdown(f"### Precio: <span style='color:green; font-weight:bold;'>${vehicle['price']:,.2f}</span>", unsafe_allow_html=True)
            st.button(f"Ver Detalles / Financiar {vehicle['id']}", key=f"details_{vehicle['id']}")
            st.markdown("---")
        
        if len(filtered_vehicles) > display_limit:
            st.info(f"Mostrando los primeros {display_limit} vehículos. Usa los filtros para refinar tu búsqueda o desplázate para ver más.")
    else:
        st.warning("No se encontraron vehículos que coincidan con tus criterios de búsqueda. Intenta ajustar los filtros.")

elif selected_page == "Comparador":
    st.info("Selecciona dos vehículos para comparar sus características lado a lado.")
    
    vehicle_options = [f"{v['make']} {v['model']} ({v['year']})" for v in DUMMY_VEHICLES]
    
    col1, col2 = st.columns(2)
    with col1:
        selected_v1_str = st.selectbox("Vehículo 1", options=vehicle_options, key="v1_select")
    with col2:
        selected_v2_str = st.selectbox("Vehículo 2", options=vehicle_options, key="v2_select")

    if st.button("Comparar"):
        v1_data = next((v for v in DUMMY_VEHICLES if f"{v['make']} {v['model']} ({v['year']})" == selected_v1_str), None)
        v2_data = next((v for v in DUMMY_VEHICLES if f"{v['make']} {v['model']} ({v['year']})" == selected_v2_str), None)

        if v1_data and v2_data:
            st.subheader(f"Comparación entre {v1_data['make']} {v1_data['model']} y {v2_data['make']} {v2_data['model']}")
            comp_col1, comp_col2 = st.columns(2)
            
            def display_vehicle_details(vehicle):
                st.write(f"**Año:** {vehicle['year']}")
                st.write(f"**Precio:** ${vehicle['price']:,.2f}")
                st.write(f"**Tipo:** {vehicle['type']}")
                st.write(f"**Combustible:** {vehicle['fuel']}")
                st.write(f"**Kilometraje:** {vehicle['mileage']:,} km")
                st.write(f"**Color:** {vehicle['color']}")
                st.write(f"**Características:** {', '.join(vehicle['features'])}")

            with comp_col1:
                st.markdown(f"### {v1_data['make']} {v1_data['model']}")
                display_vehicle_details(v1_data)
            with comp_col2:
                st.markdown(f"### {v2_data['make']} {v2_data['model']}")
                display_vehicle_details(v2_data)
        else:
            st.warning("Por favor, selecciona dos vehículos para comparar.")

# --- NEW RAG Pages ---
elif selected_page == "Ingesta de Documentos (RAG)":
    st.info("Carga documentos para enriquecer el conocimiento del Asistente AI. Los documentos se procesarán y almacenarán en la base de datos vectorial.")

    st.subheader("Cargar Documento")
    uploaded_file = st.file_uploader("Sube un archivo (PDF, TXT, MD)", type=["pdf", "txt", "md"])

    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.write(file_details)

        document_content = ""
        file_type = uploaded_file.type

        if file_type == "application/pdf":
            # Process PDF
            try:
                with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                    for page in doc:
                        document_content += page.get_text()
                st.success("PDF leído exitosamente.")
            except Exception as e:
                st.error(f"Error al leer PDF: {e}")
                document_content = None
        elif file_type == "text/plain" or file_type == "text/markdown":
            # Process TXT or MD
            document_content = uploaded_file.read().decode("utf-8")
            st.success("Archivo de texto leído exitosamente.")
        else:
            st.warning("Tipo de archivo no soportado para ingesta RAG. Por favor, sube PDF, TXT o MD.")
            document_content = None

        if document_content:
            st.subheader("Procesar y Almacenar Documento")
            chunk_size = st.slider("Tamaño de Chunks (caracteres)", 100, 2000, 1000, step=100)
            chunk_overlap = st.slider("Solapamiento de Chunks (caracteres)", 0, 500, 200, step=50)

            if st.button("Procesar y Guardar en DB Vectorial"):
                with st.spinner("Procesando documento y generando embeddings..."):
                    try:
                        # Split text into chunks
                        text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=chunk_size,
                            chunk_overlap=chunk_overlap,
                            length_function=len,
                            is_separator_regex=False,
                        )
                        chunks = text_splitter.split_text(document_content)
                        st.write(f"Documento dividido en {len(chunks)} chunks.")

                        # Add chunks to ChromaDB
                        metadatas = [{"source": uploaded_file.name, "chunk_index": i} for i in range(len(chunks))]
                        vector_store.add_texts(texts=chunks, metadatas=metadatas)
                        vector_store.persist() # Save changes to disk
                        st.success(f"¡Documento '{uploaded_file.name}' procesado y añadido a la base de datos vectorial!")
                        st.info(f"Número total de documentos/chunks en la DB: {vector_store._collection.count()}")

                    except Exception as e:
                        st.error(f"Error al procesar o guardar el documento: {e}")
                        st.info("Asegúrate de que el contenido del archivo sea válido y que el modelo de embeddings esté funcionando correctamente.")
            
    st.subheader("Documentos Cargados (Simulado)")
    # Note: ChromaDB doesn't easily expose all document contents directly without querying
    # This just shows the count, not the list of documents
    current_doc_count = vector_store._collection.count()
    if current_doc_count > 0:
        st.write(f"Actualmente hay **{current_doc_count}** chunks de documentos en la base de datos vectorial.")
        if st.button("Verificar documentos almacenados (debug)"):
            try:
                # This is a hacky way to see some content for debugging, not robust for large DBs
                # It fetches some random document IDs and then tries to get their content.
                # In a real app, you'd have a proper document management view.
                all_ids = vector_store._collection.get(include=['metadatas'])['ids']
                if all_ids:
                    sample_ids = random.sample(all_ids, min(5, len(all_ids)))
                    st.write("Muestra de IDs y metadatos:")
                    st.json(vector_store._collection.get(ids=sample_ids, include=['metadatas']))
                else:
                    st.info("No hay documentos en la base de datos para mostrar.")
            except Exception as e:
                st.error(f"Error al intentar obtener documentos para depuración: {e}")
    else:
        st.write("La base de datos vectorial está vacía. ¡Carga un documento para empezar!")
        

elif selected_page == "Asistente AI (RAG)":
    st.info("¡Hola! Soy tu asistente de Finanzauto. Ahora puedo responder preguntas basándome en la información que has cargado en la sección 'Ingesta de Documentos (RAG)'.")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for role, content in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(content)

    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        st.session_state.chat_history.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Buscando en documentos y pensando..."):
                try:
                    # 1. Retrieval: Search for relevant documents in ChromaDB
                    # You can adjust k (number of results) based on your needs
                    retrieved_docs = vector_store.similarity_search(prompt, k=3) 
                    
                    context_for_llm = ""
                    if retrieved_docs:
                        st.info(f"🔎 Documentos relevantes encontrados: {[doc.metadata.get('source', 'Desconocido') for doc in retrieved_docs]}")
                        context_for_llm = "\n\n".join([doc.page_content for doc in retrieved_docs])
                        # Add some prompt engineering to instruct the LLM to use the context
                        rag_prompt = f"""
                        Eres un asistente útil de Finanzauto. Responde la pregunta del usuario basándote únicamente en el siguiente contexto, si el contexto es relevante. Si la información no está en el contexto, indica que no puedes responder con la información proporcionada.

                        Contexto:
                        {context_for_llm}

                        Pregunta del usuario: {prompt}
                        """
                    else:
                        st.warning("🤷‍♀️ No se encontraron documentos relevantes en la base de datos. Respondiendo solo con conocimiento general.")
                        rag_prompt = prompt # Fallback to general knowledge if no docs found

                    # 2. Generation: Send context and query to LLM
                    gemini_messages = []
                    # Include a brief history for conversation flow, but the main context comes from RAG
                    for role, content in st.session_state.chat_history[-2:]: # Last 2 messages for slight conversational memory
                        if role == "user":
                            gemini_messages.append({"role": "user", "parts": [content]})
                        elif role == "assistant":
                            gemini_messages.append({"role": "model", "parts": [content]})
                    
                    # Ensure the current prompt is the last user message
                    gemini_messages.append({"role": "user", "parts": [rag_prompt]})
                    
                    chat = model.start_chat(history=[]) # Start fresh chat, context is in the prompt
                    response = chat.send_message(gemini_messages)

                    ai_response = response.text
                    st.markdown(ai_response)
                    st.session_state.chat_history.append(("assistant", ai_response))

                except Exception as e:
                    st.error(f"Lo siento, hubo un error al procesar tu solicitud con RAG. Por favor, asegúrate de que haya documentos en la DB y que el modelo de embeddings funcione. Error: {e}")
                    st.session_state.chat_history.append(("assistant", "Lo siento, hubo un error al procesar tu solicitud."))

elif selected_page == "Valoración de Vehículos Usados (IA)":
    st.info("Obtén una estimación del precio de mercado de tu vehículo usado con la ayuda de nuestra IA.")

    with st.form("vehicle_valuation_form"):
        col_val1, col_val2 = st.columns(2)
        with col_val1:
            val_make = st.selectbox("Marca", options=sorted(list(set([v['make'] for v in DUMMY_VEHICLES]))), key="val_make")
            val_year = st.slider("Año de Fabricación", min_value=1990, max_value=2024, value=2018, key="val_year")
            val_mileage = st.number_input("Kilometraje (km)", min_value=0, value=50000, step=1000, key="val_mileage")
        with col_val2:
            val_model = st.text_input("Modelo", key="val_model")
            val_condition = st.selectbox("Estado General", options=["Excelente", "Bueno", "Regular", "Necesita Reparaciones"], key="val_condition")
            val_fuel = st.selectbox("Tipo de Combustible", options=["Gasoline", "Hybrid", "Electric", "Diesel"], key="val_fuel")

        submitted_val = st.form_submit_button("Obtener Valoración")

        if submitted_val:
            with st.spinner("Analizando el mercado para tu vehículo..."):
                prompt_valuation = f"""
                Eres un tasador de vehículos para Finanzauto. Dada la siguiente información de un vehículo usado, estima su precio de mercado actual para venta o permuta. Considera que la fecha actual es 13 de julio de 2025 y que el mercado es Colombia.

                Información del Vehículo:
                - Marca: {val_make}
                - Modelo: {val_model}
                - Año: {val_year}
                - Kilometraje: {val_mileage:,} km
                - Estado General: {val_condition}
                - Tipo de Combustible: {val_fuel}

                Ofrece una valoración estimada como un rango de precios (ej. $X.XXX.XXX - $Y.YYY.YYY COP) y justifica tu estimación basándote en los factores proporcionados. También, menciona brevemente cualquier factor adicional que podría influir en el precio (ej. historial de accidentes, demanda del modelo). Utiliza valores realistas para el mercado colombiano.
                """
                try:
                    response = model.generate_content(prompt_valuation)
                    valuation_result = response.text
                    st.subheader("Valoración Estimada por IA:")
                    st.markdown(valuation_result)
                    st.success("¡Esperamos que esta valoración te sea útil!")
                except Exception as e:
                    st.error(f"Lo siento, no pude generar la valoración en este momento. Por favor, inténtalo de nuevo. Error: {e}")

elif selected_page == "Asesor de Mantenimiento (IA)":
    st.info("Pregunta a nuestra IA sobre problemas de tu vehículo, mantenimiento recomendado o costos de reparación.")

    with st.form("maintenance_advisor_form"):
        vehicle_make_model = st.text_input("Marca y Modelo de tu Vehículo (Ej: Toyota Corolla 2020)", key="maint_vehicle_model")
        problem_description = st.text_area("Describe tu pregunta o problema (Ej: 'ruido en el motor al encender', 'cuándo cambiar las bujías de un Mazda 3')", key="maint_problem_desc")
        
        submitted_maint = st.form_submit_button("Obtener Asesoría")

        if submitted_maint:
            if not vehicle_make_model or not problem_description:
                st.warning("Por favor, ingresa el modelo de tu vehículo y describe tu pregunta.")
            else:
                with st.spinner("Buscando la mejor asesoría para ti..."):
                    prompt_maintenance = f"""
                    Eres un asesor experto en mantenimiento automotriz de Finanzauto. El cliente tiene un **{vehicle_make_model}** y su pregunta/problema es: "{problem_description}".

                    Por favor, proporciona una respuesta detallada que incluya:
                    1.  Una posible causa o explicación del problema (si aplica).
                    2.  Posibles soluciones o acciones a tomar.
                    3.  Recomendaciones de mantenimiento preventivo relacionadas (si aplica).
                    4.  Una estimación general de costos si es una reparación común (ej. "puede variar entre $XXX.XXX y $YYY.YYY COP", usando formato de miles con punto y decimales con coma).
                    5.  Una advertencia para buscar un profesional si el problema es serio.
                    """
                    try:
                        response = model.generate_content(prompt_maintenance)
                        maintenance_advice = response.text
                        st.subheader("Asesoría de Mantenimiento de IA:")
                        st.markdown(maintenance_advice)
                    except Exception as e:
                        st.error(f"Lo siento, no pude generar la asesoría en este momento. Por favor, inténtalo de nuevo. Error: {e}")

elif selected_page == "Simulador de Escenarios Financieros (IA)":
    st.info("Explora cómo diferentes situaciones financieras podrían afectar tu préstamo automotriz con la ayuda de la IA.")

    st.subheader("Datos Actuales de tu Préstamo (o simulados)")
    current_loan_amount = st.number_input("Monto actual de tu préstamo automotriz ($)", min_value=1000, value=25000, step=1000, key="sim_loan_amount")
    current_monthly_payment = st.number_input("Cuota mensual actual ($)", min_value=100, value=500, step=50, key="sim_monthly_payment")
    remaining_term = st.number_input("Plazo restante (meses)", min_value=1, value=36, step=1, key="sim_remaining_term")
    current_interest_rate = st.slider("Tasa de Interés Anual actual (%)", 2.0, 15.0, 8.0, step=0.1, key="sim_interest_rate")

    st.subheader("Escenario a Simular")
    scenario_type = st.selectbox("¿Qué escenario quieres simular?", 
                                 options=["Cambio de Ingresos", "Deuda Adicional", "Pago Extra", "Refinanciamiento"], key="sim_scenario_type")

    scenario_value = 0
    if scenario_type == "Cambio de Ingresos":
        scenario_value = st.number_input("Nuevo Ingreso Mensual Neto ($) (Ej: 2500)", min_value=0, value=2000, step=100, key="sim_scenario_income")
    elif scenario_type == "Deuda Adicional":
        scenario_value = st.number_input("Monto de Nueva Deuda Mensual ($) (Ej: 200)", min_value=0, value=100, step=10, key="sim_scenario_debt")
    elif scenario_type == "Pago Extra":
        scenario_value = st.number_input("Monto de Pago Extra Único ($) (Ej: 1000)", min_value=0, value=500, step=100, key="sim_scenario_extra_payment")
    elif scenario_type == "Refinanciamiento":
        scenario_value = st.slider("Nueva Tasa de Interés Anual (%) (Ej: 6.5)", 2.0, 15.0, 6.5, step=0.1, key="sim_scenario_refi_rate")
    
    simulate_button = st.button("Simular Escenario con IA")

    if simulate_button:
        with st.spinner("Analizando tu escenario financiero..."):
            prompt_scenario = f"""
            Eres un experto en finanzas personales de Finanzauto. Necesito que simules el impacto de un escenario financiero en un préstamo automotriz existente.

            Datos del Préstamo Actual:
            - Monto Original del Préstamo (se asume que es el mismo que el "Monto actual"): ${current_loan_amount:,.2f}
            - Cuota Mensual Actual: ${current_monthly_payment:,.2f}
            - Plazo Restante: {remaining_term} meses
            - Tasa de Interés Anual Actual: {current_interest_rate:.1f}%

            Escenario a Simular:
            - Tipo de Escenario: "{scenario_type}"
            - Valor del Escenario: {scenario_value if scenario_type != "Refinanciamiento" else f"{scenario_value}%"}

            Por favor, explica claramente el impacto esperado en la cuota mensual, el plazo restante, y el interés total pagado, si aplica. Ofrece consejos prácticos sobre cómo manejar este escenario o aprovecharlo. Utiliza formato de moneda de Colombia ($ pesos con puntos para miles y comas para decimales, ej. $1.000.000,00).
            """
            try:
                response = model.generate_content(prompt_scenario)
                scenario_analysis = response.text
                st.subheader("Análisis de Escenario por IA:")
                st.markdown(scenario_analysis)
            except Exception as e:
                st.error(f"Lo siento, no pude simular el escenario en este momento. Por favor, inténtalo de nuevo. Error: {e}")

elif selected_page == "Calculadora de Impacto Ambiental":
    st.info("Estima la huella de carbono de diferentes vehículos y descubre opciones más sostenibles.")

    with st.form("environmental_impact_form"):
        col_env1, col_env2 = st.columns(2)
        with col_env1:
            env_vehicle_type = st.selectbox("Tipo de Vehículo", ["Gasolina", "Diésel", "Híbrido", "Eléctrico"], key="env_vehicle_type")
            env_mileage_year = st.number_input("Kilometraje Anual Estimado (km)", min_value=1000, value=15000, step=1000, key="env_mileage_year")
        with col_env2:
            # Adjust label and default value based on vehicle type
            if env_vehicle_type == "Eléctrico":
                env_fuel_efficiency = st.number_input("Consumo de Energía (Km/kWh)", min_value=0.1, value=5.0, step=0.1, key="env_fuel_efficiency_ev")
                env_avg_price_fuel = st.number_input("Precio promedio de la Electricidad (COP/kWh)", min_value=100, value=600, step=10, key="env_avg_price_fuel_ev")
            else:
                env_fuel_efficiency = st.number_input("Consumo de Combustible (Km/Litro)", min_value=1.0, value=12.0, step=0.1, key="env_fuel_efficiency_ice")
                env_avg_price_fuel = st.number_input("Precio promedio del Combustible (COP/Litro)", min_value=1000, value=9500, step=100, key="env_avg_price_fuel_ice")

        submitted_env = st.form_submit_button("Calcular Huella y Costo")

        if submitted_env:
            co2_emissions_kg = 0
            annual_fuel_cost = 0

            # Dummy values for CO2 per liter/kWh (approximate for Colombia)
            # CO2 emissions factors (simplified, real data varies)
            # Gasoline: ~2.3 kg CO2/liter
            # Diesel: ~2.6 kg CO2/liter
            # Electricity (Colombia mix, very roughly): ~0.2-0.4 kg CO2/kWh (can be lower due to hydro)
            if env_fuel_efficiency <= 0:
                st.error("El consumo de combustible/energía debe ser mayor que cero.")
            else:
                if env_vehicle_type == "Gasolina":
                    liters_consumed = env_mileage_year / env_fuel_efficiency
                    co2_emissions_kg = liters_consumed * 2.3 # kg CO2 per liter
                    annual_fuel_cost = liters_consumed * env_avg_price_fuel
                elif env_vehicle_type == "Diésel":
                    liters_consumed = env_mileage_year / env_fuel_efficiency
                    co2_emissions_kg = liters_consumed * 2.6 # kg CO2 per liter
                    annual_fuel_cost = liters_consumed * env_avg_price_fuel
                elif env_vehicle_type == "Híbrido":
                    # Assume 30% reduction for hybrid
                    liters_consumed = env_mileage_year / env_fuel_efficiency
                    co2_emissions_kg = liters_consumed * 2.3 * 0.7 # kg CO2 per liter (reduced)
                    annual_fuel_cost = liters_consumed * env_avg_price_fuel
                elif env_vehicle_type == "Eléctrico":
                    kwh_consumed = env_mileage_year / env_fuel_efficiency
                    co2_emissions_kg = kwh_consumed * 0.3 # kg CO2 per kWh (based on Colombian grid mix, simplified)
                    annual_fuel_cost = kwh_consumed * env_avg_price_fuel

                st.subheader("Resultados del Impacto Ambiental y Costo Anual:")
                st.success(f"**Emisiones de CO2 Anuales Estimadas:** {co2_emissions_kg:,.2f} kg")
                st.info(f"**Costo Anual Estimado de Combustible/Electricidad:** ${annual_fuel_cost:,.2f} COP")
                
                st.markdown("---")
                st.subheader("Recomendaciones para Reducir Impacto:")
                if env_vehicle_type in ["Gasolina", "Diésel"]:
                    st.write("- Considera opciones híbridas o eléctricas en tu próxima compra.")
                    st.write("- Mantén tu vehículo con un mantenimiento regular para mejorar la eficiencia.")
                    st.write("- Adopta hábitos de conducción eficientes (evita aceleraciones y frenadas bruscas).")
                elif env_vehicle_type == "Híbrido":
                    st.write("- Aprovecha al máximo el modo eléctrico de tu vehículo.")
                    st.write("- Considera la transición a un vehículo 100% eléctrico para cero emisiones directas.")
                elif env_vehicle_type == "Eléctrico":
                    st.write("- Asegúrate de cargar tu vehículo con energía de fuentes renovables si es posible (ej. paneles solares).")
                    st.write("- Sigue promoviendo la infraestructura de carga para vehículos eléctricos.")

elif selected_page == "Gamificación de Crédito":
    st.info("Completa hitos en tu proceso de crédito para ganar puntos y beneficios exclusivos.")

    if 'gamification_points' not in st.session_state:
        st.session_state.gamification_points = 0
    if 'gamification_badges' not in st.session_state:
        st.session_state.gamification_badges = []
    
    st.subheader(f"Tus Puntos Actuales: {st.session_state.gamification_points} ⭐")

    st.subheader("Hitos para Ganar Puntos:")
    
    col_game1, col_game2 = st.columns(2)

    # Milestones and their conditions (dummy, tied to session state variables)
    milestones = [
        {"name": "Perfil Completo", "desc": "Completa toda tu información en la 'Solicitud de Crédito'.", "points": 50, "condition_key": "app_first_name", "badge": "🌟 Perfil Pro"},
        {"name": "Análisis Preliminar Realizado", "desc": "Utiliza la herramienta de 'Análisis Preliminar'.", "points": 75, "condition_key": "ai_preliminary_analysis_output", "badge": "🧠 Analista Novato"},
        {"name": "Plan Recomendado", "desc": "Obtén una recomendación de plan en 'Recomendador de Planes'.", "points": 100, "condition_key": "recommended_plans_output", "badge": "💡 Planificador Experto"},
        {"name": "Solicitud Aprobada (Demo)", "desc": "Tu solicitud de crédito ha sido aprobada (simulado).", "points": 200, "condition_key": "dummy_loan_approved", "badge": "✅ Crédito Aprobado"},
    ]

    # Process milestones to update points and badges
    for milestone in milestones:
        is_completed = False
        if milestone["condition_key"] == "app_first_name":
            if st.session_state.get("app_first_name") and st.session_state.get("app_last_name"):
                is_completed = True
        elif milestone["condition_key"] == "ai_preliminary_analysis_output":
            if st.session_state.get("ai_preliminary_analysis_output"):
                is_completed = True
        elif milestone["condition_key"] == "recommended_plans_output":
            if st.session_state.get("recommended_plans_output"):
                is_completed = True
        elif milestone["condition_key"] == "dummy_loan_approved":
            # Check if any loan in the dummy data is approved
            if any(app['status'] == "Aprobada" for app in st.session_state.dummy_user_data['loan_applications']):
                is_completed = True
        
        # Only add points and badge if not already completed
        if is_completed and milestone["badge"] not in st.session_state.gamification_badges:
            st.session_state.gamification_points += milestone["points"]
            st.session_state.gamification_badges.append(milestone["badge"])
            # Rerun to update the displayed points/badges immediately after earning
            st.toast(f"¡Ganaste {milestone['points']} puntos por '{milestone['name']}' y la insignia '{milestone['badge']}'!", icon="🎉")
            st.rerun() 

    # Display milestones
    for milestone in milestones:
        is_current_completed = False
        if milestone["condition_key"] == "app_first_name":
            if st.session_state.get("app_first_name") and st.session_state.get("app_last_name"):
                is_current_completed = True
        elif milestone["condition_key"] == "ai_preliminary_analysis_output":
            if st.session_state.get("ai_preliminary_analysis_output"):
                is_current_completed = True
        elif milestone["condition_key"] == "recommended_plans_output":
            if st.session_state.get("recommended_plans_output"):
                is_current_completed = True
        elif milestone["condition_key"] == "dummy_loan_approved":
            if any(app['status'] == "Aprobada" for app in st.session_state.dummy_user_data['loan_applications']):
                is_current_completed = True

        status_emoji = "✅ Completado" if is_current_completed else "⏳ Pendiente"
        
        with col_game1:
            st.markdown(f"**{milestone['name']}**")
            st.write(f"- {milestone['desc']}")
        with col_game2:
            st.write(f"Puntos: {milestone['points']} | Estado: {status_emoji}")

    st.subheader("Tus Insignias:")
    if st.session_state.gamification_badges:
        st.write(", ".join(st.session_state.gamification_badges))
    else:
        st.write("Aún no tienes insignias. ¡Empieza a completar hitos!")

    st.markdown("---")
    st.info("Puntos y insignias son solo una simulación para demostrar la funcionalidad. Los beneficios reales se comunicarían oportunamente.")

elif selected_page == "Alertas de Vehículos":
    st.info("Configura alertas personalizadas y te notificaremos cuando vehículos que coincidan con tus criterios estén disponibles.")

    st.subheader("Configurar Nueva Alerta")
    with st.form("vehicle_alert_form"):
        alert_make = st.selectbox("Marca Preferida", options=["Cualquiera"] + sorted(list(set([v['make'] for v in DUMMY_VEHICLES]))), key="alert_make")
        alert_model = st.text_input("Modelo Específico (opcional)", key="alert_model")
        alert_max_price = st.number_input("Precio Máximo ($)", min_value=0, value=50000, step=1000, key="alert_max_price")
        alert_type = st.multiselect("Tipos de Vehículo", options=sorted(list(set([v['type'] for v in DUMMY_VEHICLES]))), key="alert_type")
        alert_email = st.text_input("Correo Electrónico para notificaciones", value=st.session_state.dummy_user_data["email"], key="alert_email")

        submitted_alert = st.form_submit_button("Crear Alerta")

        if submitted_alert:
            if not alert_email:
                st.warning("Por favor, ingresa un correo electrónico para las notificaciones.")
            else:
                new_alert = {
                    "make": alert_make,
                    "model": alert_model if alert_model else "Cualquiera",
                    "max_price": alert_max_price,
                    "type": alert_type if alert_type else "Cualquiera",
                    "email": alert_email,
                    "status": "Activa",
                    "created_date": datetime.now().strftime("%Y-%m-%d")
                }
                if 'user_alerts' not in st.session_state:
                    st.session_state.user_alerts = []
                st.session_state.user_alerts.append(new_alert)
                st.success("¡Alerta creada con éxito! Te notificaremos si encontramos vehículos que coincidan.")
                
    st.subheader("Tus Alertas Activas")
    if 'user_alerts' in st.session_state and st.session_state.user_alerts:
        for i, alert in enumerate(st.session_state.user_alerts):
            st.markdown(f"**Alerta #{i+1}**")
            st.write(f"- Marca: {alert['make']} | Modelo: {alert['model']}")
            st.write(f"- Precio Máximo: ${alert['max_price']:,.2f} | Tipo(s): {', '.join(alert['type']) if isinstance(alert['type'], list) else alert['type']}")
            st.write(f"- Estado: {alert['status']} | Creada: {alert['created_date']}")
            if alert['status'] == "Activa":
                if st.button(f"Desactivar Alerta {i+1}", key=f"deactivate_alert_{i}"):
                    st.session_state.user_alerts[i]["status"] = "Inactiva"
                    st.warning(f"Alerta #{i+1} desactivada.")
                    st.rerun()
            else:
                st.info("Esta alerta está inactiva.")
            st.markdown("---")
    else:
        st.write("Aún no tienes alertas configuradas. ¡Crea una para no perderte tu vehículo ideal!")

elif selected_page == "Portal de Clientes":
    st.info("Un espacio personalizado para que los clientes gestionen sus créditos y vehículos.")
    st.write("Aquí los clientes podrían:")
    st.markdown("- Ver el estado de sus solicitudes de crédito.")
    st.markdown("- Acceder a documentos de sus préstamos.")
    st.markdown("- Ver el historial de pagos y próximos vencimientos.")
    st.markdown("- Actualizar su información de contacto.")
    st.markdown("- Recibir ofertas personalizadas de vehículos o refinanciamientos.")

elif selected_page == "Portal de Asesores":
    st.info("Herramientas para que los asesores gestionen y den seguimiento a las solicitudes de los clientes.")
    st.write("Aquí los asesores podrían:")
    st.markdown("- Ver un listado de todas las solicitudes de crédito (nuevas, en revisión, aprobadas).")
    st.markdown("- Acceder a los detalles de cada solicitud, incluyendo el análisis preliminar de IA.")
    st.markdown("- Cargar documentos adicionales solicitados a los clientes.")
    st.markdown("- Aprobar o rechazar solicitudes, con opciones para justificar la decisión.")
    st.markdown("- Enviar comunicaciones personalizadas a los clientes.")
    st.markdown("- Acceder a métricas de rendimiento y productividad.")

elif selected_page == "Blog":
    st.info("Artículos y noticias sobre el mundo automotriz, consejos financieros y novedades de Finanzauto.")
    st.write("Explora nuestros últimos posts:")
    st.markdown("---")
    st.markdown("#### **Guía Completa para Comprar tu Primer Auto Usado**")
    st.write("Aprende todo lo que necesitas saber para hacer una compra inteligente.")
    st.write("_Publicado el: 10 de Julio, 2025_")
    st.button("Leer Más", key="blog1")
    st.markdown("---")
    st.markdown("#### **5 Razones por las que un Vehículo Eléctrico Podría Ser tu Mejor Inversión**")
    st.write("Descubre los beneficios ambientales y económicos de la movilidad eléctrica.")
    st.write("_Publicado el: 1 de Julio, 2025_")
    st.button("Leer Más", key="blog2")
    st.markdown("---")
    st.markdown("#### **Cómo Mejorar tu Historial Crediticio para Obtener Mejores Tasas**")
    st.write("Consejos prácticos para fortalecer tu perfil financiero.")
    st.write("_Publicado el: 20 de Junio, 2025_")
    st.button("Leer Más", key="blog3")
    st.markdown("---")

elif selected_page == "Soporte Multi-idioma":
    st.info("Selecciona el idioma de tu preferencia para la interfaz y el Asistente AI.")

    selected_language = st.selectbox("Idioma de la Interfaz", options=["Español", "English", "Português"], key="app_language")

    st.success(f"Idioma de la interfaz establecido a: **{selected_language}**.")
    st.write("Nota: La implementación completa del multi-idioma (traducción de todos los textos y respuestas de la IA) es una funcionalidad compleja que requiere integración profunda y servicios de traducción para el modelo de IA. Esta es una demostración conceptual.")
