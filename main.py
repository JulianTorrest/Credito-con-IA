import streamlit as st
import google.generativeai as genai
import random
import os

# --- Configuration ---
GEMINI_API_KEY = "AIzaSyCipgFWBlaeJBuAweqAh2cnOCVs1K9pLI0" # Use Streamlit secrets in production!

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
        "Premium Sound System", "Panoramic Roof", "Automatic Emergency Braking"
    ]

    vehicles = []
    for i in range(1, num_vehicles + 1):
        make = random.choice(makes)
        model = random.choice(models_by_make.get(make, ["Generic Model"])) # Get model specific to make, or default
        year = random.randint(2018, 2025)
        
        base_price = random.randint(15000, 80000)
        if "BMW" in make or "Mercedes-Benz" in make or "Audi" in make or "Tesla" in make:
            base_price = random.randint(35000, 120000)
        price = base_price + (year - 2018) * random.uniform(500, 2000) + random.uniform(-1000, 1000) # Adjust price by year
        price = max(10000, price) # Ensure minimum price
        
        v_type = random.choice(vehicle_types)
        fuel = random.choice(fuel_types)
        
        if v_type == "EV":
            fuel = "Electric"
            price = random.randint(35000, 90000) # EVs tend to be more expensive

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

# Generate a large number of random vehicles
DUMMY_VEHICLES = generate_random_vehicles(num_vehicles=5000)

# --- Simulate User Data for Dashboard (for a single dummy user) ---
# In a real app, this would come from a database after user login
if 'dummy_user_data' not in st.session_state:
    st.session_state.dummy_user_data = {
        "name": "Juan Pérez",
        "email": "juan.perez@example.com",
        "loan_applications": [
            {"id": "APP001", "vehicle": "Toyota RAV4 2023", "amount": 32000, "status": "Aprobada", "date": "2025-06-01"},
            {"id": "APP002", "vehicle": "Ford F-150 2022", "amount": 45000, "status": "En Revisión", "date": "2025-07-10"},
            {"id": "APP003", "vehicle": "Tesla Model 3 2024", "amount": 40000, "status": "Rechazada", "date": "2025-05-15", "reason": "Ingresos insuficientes"},
        ],
        "favorite_vehicles": random.sample(DUMMY_VEHICLES, k=3), # Select 3 random vehicles as favorites
        "recommended_vehicles": random.sample(DUMMY_VEHICLES, k=2) # Placeholder for AI recommendations
    }

# --- Streamlit App Structure ---
st.set_page_config(layout="wide", page_title="Finanzauto", initial_sidebar_state="expanded")

st.title("🚗 Finanzauto: Tu Portal de Vehículos y Financiamiento")

# --- Sidebar Navigation ---
st.sidebar.title("Menú Principal")
page = st.sidebar.radio("Navegación", [
    "Asistente AI",
    "Dashboard",
    "Simulador de Crédito",
    "Solicitud de Crédito",
    "Análisis Preliminar",
    "Recomendador",
    "Catálogo de Vehículos",
    "Comparador",
    "Subastas",
    "Portal de Clientes",
    "Portal de Asesores",
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
                    
                    # Ensure chat history is correctly formatted for Gemini
                    if not gemini_messages: # Should not happen with prompt, but safety check
                        response = model.generate_content(prompt)
                    else:
                        # Exclude the very last user message from history if it's the current prompt
                        # This prevents sending the prompt twice (once in history, once as current message)
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

    user_data = st.session_state.dummy_user_data

    st.subheader("Estado de tus Solicitudes de Crédito")
    if user_data["loan_applications"]:
        for app in user_data["loan_applications"]:
            status_emoji = "✅" if app["status"] == "Aprobada" else "⏳" if app["status"] == "En Revisión" else "❌"
            st.markdown(f"- **Solicitud {app['id']}:** Vehículo: {app['vehicle']} | Monto: ${app['amount']:,.2f} | Estado: **{status_emoji} {app['status']}** ({app['date']})")
            if "reason" in app:
                st.info(f"    *Razón:* {app['reason']}")
        st.markdown("---")
    else:
        st.write("No tienes solicitudes de crédito recientes.")

    st.subheader("Tus Vehículos Favoritos")
    if user_data["favorite_vehicles"]:
        for fav_car in user_data["favorite_vehicles"]:
            st.markdown(f"- **{fav_car['year']} {fav_car['make']} {fav_car['model']}** (Precio: ${fav_car['price']:,.2f})")
            st.markdown(f"  *Tipo: {fav_car['type']}, Combustible: {fav_car['fuel']}*")
        st.markdown("---")
    else:
        st.write("Aún no has marcado ningún vehículo como favorito.")

    st.subheader("Recomendaciones Personalizadas para Ti")
    st.write("Basado en tus intereses y actividad, estas son algunas recomendaciones:")
    if user_data["recommended_vehicles"]:
        for rec_car in user_data["recommended_vehicles"]:
            st.markdown(f"- **{rec_car['year']} {rec_car['make']} {rec_car['model']}** (Precio: ${rec_car['price']:,.2f})")
            st.markdown(f"  *Ideal para: [Explicación generada por IA en la sección de Recomendador]*")
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
        # Store these in session state for Preliminary Analysis to access
        st.session_state.income = st.number_input("Ingresos Mensuales Netos ($)", min_value=0, value=2000, key="app_income")
        st.session_state.existing_debts = st.number_input("Deudas Mensuales Existentes ($)", min_value=0, value=500, key="app_existing_debts")
        st.session_state.desired_vehicle_price = st.number_input("Precio del Vehículo Deseado ($)", min_value=0, value=30000, key="app_desired_vehicle_price")
        
        submitted = st.form_submit_button("Enviar Solicitud")
        if submitted:
            if not first_name or not last_name or not email:
                st.warning("Por favor, completa todos los campos obligatorios.")
            else:
                st.success(f"Solicitud recibida para {first_name} {last_name}. Un asesor se pondrá en contacto pronto.")
                # You could also append this to st.session_state.dummy_user_data['loan_applications']
                # for dynamic display on the dashboard, but for simplicity, we just display it here.
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

    # Retrieve data from session state (populated by "Solicitud de Crédito" form)
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
                    # Define dummy credit rules for Gemini to interpret
                    credit_rules_prompt = """
                    Reglas de elegibilidad generales para un préstamo automotriz:
                    1. La relación Ingresos/Deudas (DTI) después de la posible cuota del vehículo idealmente no debe exceder el 40%.
                    2. Un buen indicador de capacidad de pago es que el ingreso neto sea al menos 3 veces el pago mensual estimado.
                    3. El precio del vehículo deseado no debe ser excesivamente alto en comparación con los ingresos.
                    4. Se valora un ingreso neto superior a $1,500 USD mensuales.
                    """

                    # Estimate a dummy monthly payment for the desired vehicle based on a generic rate/term
                    # This is a simplification; a real system would use a more accurate estimate or credit scoring.
                    estimated_monthly_payment = (desired_vehicle_price * 0.08 / 12) / (1 - (1 + 0.08 / 12)**-(60)) # 8% annual, 60 months

                    # Craft the prompt for Gemini
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


elif page == "Recomendador":
    st.header("💡 Recomendador de Vehículos")
    st.info("Describe el vehículo de tus sueños y te ayudaremos a encontrarlo.")
    user_preferences = st.text_area("Cuéntanos qué tipo de vehículo buscas (ej: 'Necesito un SUV familiar, eficiente en combustible y con buen espacio de carga'):")
    
    if st.button("Buscar Recomendaciones"):
        if user_preferences:
            st.write(f"Analizando tus preferencias: '{user_preferences}'...")
            
            with st.spinner("Buscando recomendaciones con IA..."):
                try:
                    # Craft a prompt for Gemini to act as a recommender
                    prompt_for_gemini = f"""
                    Eres un experto en vehículos y finanzas. Te proporcionaré una descripción de las preferencias de un cliente para un vehículo.
                    Basado en la siguiente lista de vehículos disponibles, por favor, recomienda 3-5 vehículos que mejor se ajusten a sus necesidades.
                    Para cada recomendación, explica brevemente por qué es una buena opción basada en sus preferencias.

                    Preferencias del cliente: "{user_preferences}"

                    Lista de vehículos disponibles (solo los primeros 200 para relevancia y evitar sobrecarga de tokens):
                    {DUMMY_VEHICLES[:200]}

                    Formato de respuesta deseado:
                    **Recomendaciones de Vehículos:**
                    - **[Año] [Marca] [Modelo]:** [Breve explicación de por qué es recomendado].
                    - **[Año] [Marca] [Modelo]:** [Breve explicación de por qué es recomendado].
                    ...
                    """
                    
                    response = model.generate_content(prompt_for_gemini)
                    ai_recommendations = response.text
                    
                    st.subheader("Recomendaciones de la IA:")
                    st.markdown(ai_recommendations)
                    
                except Exception as e:
                    st.error(f"Lo siento, hubo un error al generar las recomendaciones. Por favor, inténtalo de nuevo. Error: {e}")
        else:
            st.warning("Por favor, describe tus preferencias para recibir recomendaciones.")


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
    st.info("Acceso para clientes existentes para ver el estado de sus préstamos y gestionar su cuenta.")
    st.text_input("Usuario")
    st.text_input("Contraseña", type="password")
    st.button("Ingresar (Dummy)")


elif page == "Portal de Asesores":
    st.header("💼 Portal de Asesores")
    st.info("Acceso exclusivo para nuestros asesores de Finanzauto.")
    st.text_input("Usuario del Asesor")
    st.text_input("Contraseña del Asesor", type="password")
    st.button("Ingresar (Dummy)")

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
