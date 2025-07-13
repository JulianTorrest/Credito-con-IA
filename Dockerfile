# Usa una imagen base oficial de Python.
# Optamos por una imagen ligera (slim-bullseye) para reducir el tamaño final del contenedor.
FROM python:3.10-slim-bullseye

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requerimientos primero para aprovechar el cache de Docker.
# Si requirements.txt no cambia, Docker no volverá a ejecutar la instalación de pip.
COPY requirements.txt .

# Instala las dependencias Python.
# `--no-cache-dir`: No guarda los paquetes descargados, reduciendo el tamaño de la imagen.
# `requirements.txt`: Contiene todas las librerías Python necesarias.
RUN pip install --no-cache-dir -r requirements.txt

# Instala dependencias del sistema operativo necesarias para PyMuPDF (fitz)
# Estas son librerías que PyMuPDF necesita para funcionar correctamente con PDF.
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libfontconfig1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copia el resto de tu código de la aplicación al directorio de trabajo.
# Esto incluye main.py y cualquier otro archivo necesario.
COPY . .

# Crea el directorio para ChromaDB si no existe.
# Aunque Chroma lo crearía, es una buena práctica asegurar que el contenedor tenga los permisos.
RUN mkdir -p chroma_db

# Permite que Streamlit escuche en todas las interfaces de red, no solo localhost.
# Esto es esencial para que la app sea accesible desde fuera del contenedor.
ENV STREAMLIT_SERVER_PORT=8501
EXPOSE 8501

# Comando para ejecutar la aplicación Streamlit cuando el contenedor inicie.
# `--server.port $STREAMLIT_SERVER_PORT`: Usa la variable de entorno para el puerto.
# `--server.enableCORS false`: Importante para evitar problemas de CORS si la aplicación se accede desde otro origen.
# `--server.enableXsrfProtection false`: Recomendado para entornos de desarrollo/pruebas con Streamlit Cloud.
CMD ["streamlit", "run", "main.py", "--server.port", "8501", "--server.enableCORS", "false", "--server.enableXsrfProtection", "false"]
