import streamlit as st
import google.generativeai as genai
import random
import os

# --- Configuration ---
# IMPORTANT: In a real application, secure your API key using Streamlit secrets.
# Create a .streamlit/secrets.toml file with: GEMINI_API_KEY="your_api_key_here"
# Then access it via st.secrets["GEMINI_API_KEY"]
GEMINI_API_KEY = "AIzaSyCipgFWBlaeJBuAweqAh2cnOCVs1K9pLI0" # Dummy key. REPLACE THIS!

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the generative model
model = genai.GenerativeModel('gemini-pro')

# --- Dummy Data Generation (Dynamic) ---
@st.cache_data # Cache the generated data to avoid re-generating on every rerun
def generate_random_vehicles(num_vehicles=5000): # Default to 5000 vehicles
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
        "Premium Sound System", "Panoramic Roof", "Automatic Emergency BrakING"
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
# This check ensures dummy_user_data is properly initialized or re-initialized if needed.
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
# This button helps clear session state during development to prevent stale data issues.
# REMOVE or COMMENT OUT this block in production to avoid losing user data!
if st.sidebar.button("Reiniciar Datos de la App (Desarrollo)"):
    st.session_state.clear()
    st.cache_data.clear()
    st.rerun() # Corrected: Use st.rerun() instead of st.experimental_rerun()

# --- Sidebar Navigation ---
st.sidebar.title("Menú Principal")
page = st.sidebar.radio("Navegación", [
    "Asistente AI",
    "Dashboard",
    "Simulador de Crédito",
    "Solicitud de Crédito",
    "Análisis Preliminar",
    "Recomendador de Planes", # Renamed
    "Catálogo de Vehículos",
    "Comparador",
    "Subastas",
    "Portal de Clientes", # No login
    "Portal de Asesores", # No login
    "Blog"
])

# --- Page Content Based on Selection ---

if page == "Asistente AI":
    st.header("🤖 Asistente AI")
    st.write("¡Hola! Soy tu asistente de Finanzauto. ¿En qué puedo ayudarte hoy?")

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
            with st.spinner("Pensando..."):
                try:
                    gemini_messages = []
                    for role, content in st.session_state.chat_history:
                        if role == "user" and content == prompt:
                            gemini_messages.append({"role": "user", "parts": [content]})
                        elif role == "user":
                            gemini_messages.append({"role": "user", "parts": [content]})
                        elif role == "assistant":
                            gemini_messages.append({"role": "model", "parts": [content]})
                    
                    if not gemini_messages:
                         response = model.generate_content(prompt)
                    else:
                        if gemini_messages[-1]["role"] == "user" and gemini_messages[-1]["parts"][0] == prompt:
                             chat_history_for_gemini = gemini_messages[:-1]
                        else:
                             chat_history_for_gemini = gemini_messages

                        chat = model.start_chat(history=chat_history_for_gemini)
                        response = chat.send_message(prompt)

                    ai_response = response.text
                    st.markdown(ai_response)
                    st.session_state.chat_history.append(("assistant", ai_response))
                except Exception as e:
                    st.error(f"Lo siento, hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo. Error: {e}")
                    st.session_state.chat_history.append(("assistant", "Lo siento, hubo un error al procesar tu solicitud."))

elif page == "Dashboard":
    st.header("📊 Dashboard del Usuario")
    st.info("¡Bienvenido, Juan Pérez! Aquí tienes un resumen de tu actividad en Finanzauto.")

    # Ensure user_data is freshly loaded from session state (or re-initialized)
    user_data = st.session_state.dummy_user_data

    # --- Tabs for Loan Stages ---
    tab_titles = ["Todas las Solicitudes", "En Análisis/Revisión", "Documentos Pendientes", "Aprobadas", "Firmado/Desembolsado", "Rechazadas"]
    tabs = st.tabs(tab_titles)

    # Filter applications by stage for each tab
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
                    # Using .get() for safety here too, though the dummy data should have these.
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

elif page == "Simulador de Crédito":
    st.header("💰 Simulador de Crédito")
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

elif page == "Solicitud de Crédito":
    st.header("📝 Solicitud de Crédito")
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
                    "deudas_existentes": st.session_state.existing_debts,
                    "precio_vehiculo_deseado": st.session_state.desired_vehicle_price
                })

elif page == "Análisis Preliminar":
    st.header("🔎 Análisis Preliminar de Crédito")
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
                    """
                    
                    response = model.generate_content(prompt_for_gemini)
                    ai_analysis = response.text

                    st.subheader("Resultados del Análisis Preliminar de IA:")
                    st.markdown(ai_analysis)

                except Exception as e:
                    st.error(f"Lo siento, hubo un error al realizar el análisis. Por favor, inténtalo de nuevo. Error: {e}")

elif page == "Recomendador de Planes": # Renamed page
    st.header("💡 Recomendador de Planes Financieros")
    st.info("Cuéntanos sobre tus objetivos y te ayudaremos a encontrar el plan de financiamiento ideal.")
    
    plan_preferences = st.text_area(
        "Describe tu situación financiera y tus objetivos para un préstamo automotriz (ej: 'Busco la cuota mensual más baja posible', 'Quiero pagar el préstamo rápidamente', 'Necesito un plan flexible con opciones de refinanciamiento'):",
        key="plan_reco_prompt"
    )

    if st.button("Buscar Recomendaciones de Planes"):
        if plan_preferences:
            st.write(f"Analizando tus preferencias de plan: '{plan_preferences}'...")
            
            with st.spinner("Buscando recomendaciones de planes con IA..."):
                try:
                    # Define dummy loan plan types for Gemini to consider
                    dummy_loan_plans = [
                        {"name": "Plan Estándar", "description": "Tasa fija, plazos de 3 a 6 años, pagos mensuales consistentes."},
                        {"name": "Plan Flexi-Pago", "description": "Tasa fija, plazos extendidos hasta 7 años, pagos iniciales más bajos con opción de abonos extraordinarios."},
                        {"name": "Plan Joven Conductor", "description": "Dirigido a primeros compradores, tasas competitivas, posibilidad de incluir seguro en cuota."},
                        {"name": "Plan Eco-Auto", "description": "Beneficios especiales para vehículos híbridos y eléctricos, tasas preferenciales, plazos de 5 a 8 años."},
                        {"name": "Plan Plus", "description": "Para clientes con buen historial, tasas muy bajas, plazos cortos a medios (1-4 años), requiere enganche alto."}
                    ]

                    prompt_for_gemini = f"""
                    Eres un asesor financiero de Finanzauto especializado en préstamos automotrices.
                    Un cliente te ha dado sus preferencias para un plan de financiamiento.
                    Basándote en sus preferencias y en la siguiente descripción de nuestros planes de préstamo dummy, recomienda 2-3 planes que mejor se adapten a sus necesidades.
                    Explica por qué cada plan es una buena opción para sus objetivos.

                    Preferencias del cliente: "{plan_preferences}"

                    Nuestros planes de préstamo disponibles:
                    {dummy_loan_plans}

                    Formato de respuesta deseado:
                    **Recomendaciones de Planes de Financiamiento:**
                    - **[Nombre del Plan]:** [Breve explicación de por qué es recomendado para las preferencias del cliente].
                    - **[Nombre del Plan]:** [Breve explicación de por qué es recomendado para las preferencias del cliente].
                    ...
                    """
                    
                    response = model.generate_content(prompt_for_gemini)
                    ai_recommendations = response.text
                    
                    st.subheader("Recomendaciones de Planes de Financiamiento por la IA:")
                    st.markdown(ai_recommendations)
                    
                except Exception as e:
                    st.error(f"Lo siento, hubo un error al generar las recomendaciones de planes. Por favor, inténtalo de nuevo. Error: {e}")
        else:
            st.warning("Por favor, describe tus preferencias para recibir recomendaciones de planes.")

elif page == "Catálogo de Vehículos":
    st.header("🚗 Catálogo de Vehículos")
    st.info(f"Explora nuestra selección de {len(DUMMY_VEHICLES):,} vehículos disponibles.")

    st.subheader("Filtros y Búsqueda")
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        search_query = st.text_input("Buscar por Marca o Modelo", "", key="catalog_search_query")
        min_price = st.number_input("Precio Mínimo ($)", min_value=0, value=0, step=1000, key="catalog_min_price")
    with col_filter2:
        max_price = st.number_input("Precio Máximo ($)", min_value=0, value=150000, step=1000, key="catalog_max_price")
        selected_types = st.multiselect("Tipo de Vehículo", options=sorted(list(set([v['type'] for v in DUMMY_VEHICLES]))), key="catalog_types")
    with col_filter3:
        selected_fuels = st.multiselect("Tipo de Combustible", options=sorted(list(set([v['fuel'] for v in DUMMY_VEHICLES]))), key="catalog_fuels")
        selected_year = st.slider("Año Mínimo", min_value=2018, max_value=2025, value=2018, key="catalog_year")

    filtered_vehicles = []
    for vehicle in DUMMY_VEHICLES:
        match = True
        if search_query:
            if search_query.lower() not in vehicle['make'].lower() and \
               search_query.lower() not in vehicle['model'].lower():
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
    
    st.write(f"Mostrando {len(filtered_vehicles):,} de {len(DUMMY_VEHICLES):,} vehículos.")

    display_limit = 200
    for vehicle in filtered_vehicles[:display_limit]:
        st.subheader(f"{vehicle['year']} {vehicle['make']} {vehicle['model']}")
        st.write(f"**Tipo:** {vehicle['type']} | **Combustible:** {vehicle['fuel']} | **Kilometraje:** {vehicle['mileage']:,} km")
        st.write(f"**Color:** {vehicle['color']} | **Características:** {', '.join(vehicle['features'])}")
        st.write(f"**Precio:** ${vehicle['price']:,.2f}")
        st.markdown("---")
    
    if len(filtered_vehicles) > display_limit:
        st.info(f"Mostrando los primeros {display_limit} vehículos. Usa los filtros para refinar tu búsqueda.")

elif page == "Comparador":
    st.header("⚖️ Comparador de Vehículos")
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

elif page == "Subastas":
    st.header("🔨 Subastas de Vehículos")
    st.info("Participa en nuestras subastas de vehículos exclusivos.")
    st.write("No hay subastas activas en este momento (dummy).")

elif page == "Portal de Clientes":
    st.header("👤 Portal de Clientes")
    st.info("Bienvenido al portal de clientes. Aquí puedes gestionar tus préstamos y ver tu historial.")
    user_data = st.session_state.dummy_user_data
    
    st.subheader(f"Información de Cuenta de {user_data['name']}")
    st.write(f"**Correo Electrónico:** {user_data['email']}")
    st.markdown("---")

    st.subheader("Mis Préstamos Actuales")
    # Filter for approved/active loans
    active_loans = [app for app in user_data["loan_applications"] if app.get("status") == "Aprobada" or app.get("stage") == "Desembolsado" or app.get("stage") == "Firma de Contrato"]
    if active_loans:
        for loan in active_loans:
            st.markdown(f"**Préstamo {loan.get('id', 'N/A')}** para **{loan.get('vehicle', 'N/A')}**")
            st.write(f"- Monto: ${loan.get('amount', 0):,.2f}")
            st.write(f"- Estado: **{loan.get('status', 'Desconocido')}** / Etapa: **{loan.get('stage', 'Desconocida')}**")
            st.write(f"- Fecha de Aprobación/Inicio: {loan.get('date', 'N/A')}")
            # Dummy details for a loan
            st.write(f"- Cuota Mensual Estimada: ${random.randint(500,1500):,.2f}")
            st.write(f"- Saldo Pendiente (Dummy): ${random.randint(5000, loan.get('amount', 50000)-1000):,.2f}") # Ensure amount is not zero
            st.markdown("---")
    else:
        st.write("No tienes préstamos activos en este momento.")

    st.subheader("Historial de Solicitudes (Completo)")
    if user_data["loan_applications"]:
        for app in user_data["loan_applications"]:
            status_emoji = "✅" if app.get("status") == "Aprobada" else "⏳" if app.get("status") == "En Revisión" else "❌"
            st.markdown(f"- **{app.get('id', 'N/A')}:** {app.get('vehicle', 'N/A')} | Monto: ${app.get('amount', 0):,.2f} | Estado: **{status_emoji} {app.get('status', 'Desconocido')}** | Etapa: _{app.get('stage', 'Desconocida')}_ ({app.get('date', 'N/A')})")
            if "reason" in app:
                st.info(f"    *Razón:* {app['reason']}")
        st.markdown("---")
    else:
        st.write("No hay historial de solicitudes.")

elif page == "Portal de Asesores":
    st.header("💼 Portal de Asesores")
    st.info("Bienvenido al portal de asesores. Aquí puedes gestionar solicitudes y clientes.")
    
    # Simulate a list of all applications for advisors to review
    all_applications = st.session_state.dummy_user_data["loan_applications"] + [
        {"id": "ADV001", "vehicle": "Audi Q5 2023", "amount": 55000, "status": "Pendiente", "stage": "Análisis Preliminar", "date": "2025-07-13", "applicant": "María García"},
        {"id": "ADV002", "vehicle": "Volkswagen ID.4 2024", "amount": 42000, "status": "Pendiente", "stage": "Documentación Enviada", "date": "2025-07-11", "applicant": "Pedro Gómez"}
    ]

    st.subheader("Solicitudes Pendientes de Revisión")
    pending_applications = [app for app in all_applications if app.get("status") == "En Revisión" or app.get("status") == "Pendiente" or app.get("stage") == "Análisis Preliminar" or app.get("stage") == "Recopilación de Documentos"]
    
    if pending_applications:
        for app in pending_applications:
            st.markdown(f"**ID: {app.get('id', 'N/A')}** | **Vehículo:** {app.get('vehicle', 'N/A')} | **Monto:** ${app.get('amount', 0):,.2f}")
            st.write(f"**Solicitante:** {app.get('applicant', st.session_state.dummy_user_data['name'])}")
            st.write(f"**Estado:** {app.get('status', 'Desconocido')} | **Etapa:** {app.get('stage', 'Desconocida')} | **Fecha:** {app.get('date', 'N/A')}")
            st.button(f"Revisar Solicitud {app.get('id', 'N/A')}", key=f"review_{app.get('id', 'N/A')}")
            st.markdown("---")
    else:
        st.write("No hay solicitudes pendientes de revisión en este momento.")

    st.subheader("Estadísticas de Asesores (Dummy)")
    st.metric(label="Solicitudes Aprobadas (Mes)", value="15")
    st.metric(label="Solicitudes en Proceso", value="8")
    st.metric(label="Monto Total Aprobado (Mes)", value="$450,000")

elif page == "Blog":
    st.header("✍️ Blog de Finanzauto")
    st.info("Artículos, noticias y consejos sobre el mundo automotriz y el financiamiento.")
    st.subheader("Últimos Artículos (Dummy)")
    st.markdown("""
    ---
    ### **5 Consejos para Comprar tu Primer Auto**
    *Por: Equipo Finanzauto | 10 de Julio, 2025*
    Descubre cómo hacer una compra inteligente...
    [Leer más](dummy_link_1)
    ---
    ### **El Futuro de los Vehículos Eléctricos en Colombia**
    *Por: Analista Invitado | 5 de Julio, 2025*
    Un vistazo a las tendencias y oportunidades...
    [Leer más](dummy_link_2)
    ---
    """)
