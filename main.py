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
        # Price logic: higher for newer luxury cars, lower for older economy cars
        base_price = random.randint(15000, 80000)
        if "BMW" in make or "Mercedes-Benz" in make or "Audi" in make or "Tesla" in make:
            base_price = random.randint(35000, 120000)
        price = base_price + (year - 2018) * 2000 + random.randint(-2000, 2000) # Adjust price by year
        price = max(10000, price) # Ensure minimum price
        
        v_type = random.choice(vehicle_types)
        fuel = random.choice(fuel_types)
        
        # Ensure EVs are electric fuel type
        if v_type == "EV":
            fuel = "Electric"
            price = random.randint(35000, 90000) # EVs tend to be more expensive

        # Select a random number of features
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
            "mileage": random.randint(500, 150000) if year < 2025 else random.randint(10, 5000), # Lower mileage for newer cars
            "color": random.choice(["White", "Black", "Silver", "Red", "Blue", "Gray", "Green", "Yellow"])
        })
    return vehicles

# Generate a large number of random vehicles
DUMMY_VEHICLES = generate_random_vehicles(num_vehicles=5000) # You can adjust this number

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

    # Display chat messages from history
    for role, content in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(content)

    # Chat input
    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        st.session_state.chat_history.append(("user", prompt))
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                try:
                    # Pass the full chat history to Gemini for context
                    # Gemini expects messages in a specific format for context: [{"role": "user", "parts": ["text"]}, {"role": "model", "parts": ["text"]}]
                    
                    # Convert st.session_state.chat_history to Gemini's expected format
                    gemini_messages = []
                    for role, content in st.session_state.chat_history:
                        # For the current user prompt, ensure it's the last one and not duplicated
                        if role == "user" and content == prompt:
                            gemini_messages.append({"role": "user", "parts": [content]})
                        elif role == "user":
                            gemini_messages.append({"role": "user", "parts": [content]})
                        elif role == "assistant":
                            gemini_messages.append({"role": "model", "parts": [content]})

                    # Only pass the *current* prompt if there's no history, otherwise pass the history
                    if not st.session_state.chat_history:
                         response = model.generate_content(prompt)
                    else:
                        chat = model.start_chat(history=gemini_messages[:-1]) # Exclude the current user prompt from history
                        response = chat.send_message(prompt) # Send the current user prompt

                    ai_response = response.text
                    st.markdown(ai_response)
                    st.session_state.chat_history.append(("assistant", ai_response))
                except Exception as e:
                    st.error(f"Lo siento, hubo un error al procesar tu solicitud. Por favor, inténtalo de nuevo. Error: {e}")
                    st.session_state.chat_history.append(("assistant", "Lo siento, hubo un error al procesar tu solicitud."))


elif page == "Dashboard":
    st.header("📊 Dashboard del Usuario")
    st.info("Aquí verás un resumen de tus solicitudes, vehículos favoritos y recomendaciones personalizadas.")
    st.write("*(Esta sección se expandirá con datos reales una vez tengamos el portal de clientes funcionando.)*")

elif page == "Simulador de Crédito":
    st.header("💰 Simulador de Crédito")
    st.write("Calcula tus pagos estimados.")
    # Dummy simulator inputs
    loan_amount = st.slider("Monto del Préstamo ($)", 5000, 100000, 30000, step=1000)
    loan_term_years = st.slider("Plazo (años)", 1, 7, 5)
    interest_rate = st.slider("Tasa de Interés Anual (%)", 2.0, 15.0, 7.5, step=0.1)

    if st.button("Calcular"):
        # Simple interest calculation for demo
        monthly_rate = (interest_rate / 100) / 12
        num_payments = loan_term_years * 12
        if monthly_rate > 0:
            monthly_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate)**-num_payments)
        else: # Handle 0 interest rate
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
            first_name = st.text_input("Nombre(s)")
            email = st.text_input("Correo Electrónico")
        with col2:
            last_name = st.text_input("Apellido(s)")
            phone = st.text_input("Teléfono")

        st.subheader("Información Financiera (Dummy)")
        income = st.number_input("Ingresos Mensuales Netos ($)", min_value=0, value=2000)
        existing_debts = st.number_input("Deudas Mensuales Existentes ($)", min_value=0, value=500)
        desired_vehicle_price = st.number_input("Precio del Vehículo Deseado ($)", min_value=0, value=30000)

        submitted = st.form_submit_button("Enviar Solicitud (Dummy)")
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
                    "ingresos": income,
                    "deudas_existentes": existing_debts,
                    "precio_vehiculo_deseado": desired_vehicle_price
                })

elif page == "Análisis Preliminar":
    st.header("🔎 Análisis Preliminar de Crédito")
    st.info("Aquí se mostrará un análisis automatizado inicial de tu elegibilidad, basado en la información que proporciones.")
    st.write("*(Integración con Gemini para evaluación se implementará aquí.)*")

elif page == "Recomendador":
    st.header("💡 Recomendador de Vehículos")
    st.info("Describe el vehículo de tus sueños y te ayudaremos a encontrarlo.")
    user_preferences = st.text_area("Cuéntanos qué tipo de vehículo buscas (ej: 'Necesito un SUV familiar, eficiente en combustible y con buen espacio de carga'):")
    
    if st.button("Buscar Recomendaciones"):
        if user_preferences:
            st.write(f"Analizando tus preferencias: '{user_preferences}'...")
            
            # --- Gemini Integration for Recommendations ---
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

    # Add search and filter options for a large catalog
    st.subheader("Filtros y Búsqueda")
    col_filter1, col_filter2, col_filter3 = st.columns(3)

    with col_filter1:
        search_query = st.text_input("Buscar por Marca o Modelo", "")
        min_price = st.number_input("Precio Mínimo ($)", min_value=0, value=0, step=1000)
    with col_filter2:
        max_price = st.number_input("Precio Máximo ($)", min_value=0, value=150000, step=1000)
        selected_types = st.multiselect("Tipo de Vehículo", options=list(set([v['type'] for v in DUMMY_VEHICLES])))
    with col_filter3:
        selected_fuels = st.multiselect("Tipo de Combustible", options=list(set([v['fuel'] for v in DUMMY_VEHICLES])))
        selected_year = st.slider("Año Mínimo", min_value=2018, max_value=2025, value=2018)

    filtered_vehicles = []
    for vehicle in DUMMY_VEHICLES:
        match = True
        # Text search
        if search_query:
            if search_query.lower() not in vehicle['make'].lower() and \
               search_query.lower() not in vehicle['model'].lower():
                match = False
        # Price filter
        if not (min_price <= vehicle['price'] <= max_price):
            match = False
        # Type filter
        if selected_types and vehicle['type'] not in selected_types:
            match = False
        # Fuel filter
        if selected_fuels and vehicle['fuel'] not in selected_fuels:
            match = False
        # Year filter
        if vehicle['year'] < selected_year:
            match = False

        if match:
            filtered_vehicles.append(vehicle)
    
    st.write(f"Mostrando {len(filtered_vehicles):,} de {len(DUMMY_VEHICLES):,} vehículos.")

    # Display filtered vehicles (limit for performance in demo)
    display_limit = 200 # Only display a subset for performance
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
    
    # Use the generated DUMMY_VEHICLES for options
    vehicle_options = [f"{v['make']} {v['model']} ({v['year']})" for v in DUMMY_VEHICLES]
    
    col1, col2 = st.columns(2)
    with col1:
        selected_v1_str = st.selectbox("Vehículo 1", options=vehicle_options, key="v1_select")
    with col2:
        selected_v2_str = st.selectbox("Vehículo 2", options=vehicle_options, key="v2_select")

    if st.button("Comparar"):
        # Find the actual vehicle dictionaries based on the selected strings
        v1_data = next((v for v in DUMMY_VEHICLES if f"{v['make']} {v['model']} ({v['year']})" == selected_v1_str), None)
        v2_data = next((v for v in DUMMY_VEHICLES if f"{v['make']} {v['model']} ({v['year']})" == selected_v2_str), None)

        if v1_data and v2_data:
            st.subheader(f"Comparación entre {v1_data['make']} {v1_data['model']} y {v2_data['make']} {v2_data['model']}")
            comp_col1, comp_col2 = st.columns(2)
            
            # Common display function for comparison details
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
    st.write("*(Esta sección mostrará vehículos en subasta con información de pujas.)*")
    st.write("No hay subastas activas en este momento (dummy).")


elif page == "Portal de Clientes":
    st.header("👤 Portal de Clientes")
    st.info("Acceso para clientes existentes para ver el estado de sus préstamos y gestionar su cuenta.")
    st.write("*(Funcionalidad de inicio de sesión y gestión de cuenta se implementará aquí.)*")
    st.text_input("Usuario")
    st.text_input("Contraseña", type="password")
    st.button("Ingresar (Dummy)")


elif page == "Portal de Asesores":
    st.header("💼 Portal de Asesores")
    st.info("Acceso exclusivo para nuestros asesores de Finanzauto.")
    st.write("*(Funcionalidad de inicio de sesión y herramientas para asesores se implementará aquí.)*")
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
