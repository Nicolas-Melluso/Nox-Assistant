# Dockerfile para custom-voice-assistant
# Imagen base oficial de Python
FROM python:3.10-slim

# Variables de entorno para evitar prompts interactivos y mejorar logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependencias del sistema necesarias para spaCy y dateparser
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y archivos del proyecto
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt


# Instalar modelo spaCy español (es_core_news_sm) compatible con spaCy 3.5.4
RUN pip install https://github.com/explosion/spacy-models/releases/download/es_core_news_sm-3.5.0/es_core_news_sm-3.5.0-py3-none-any.whl \
    && python -m spacy link es_core_news_sm es_core_news_sm

# Copiar el resto del código fuente
COPY . .


# Permitir cambiar el comando por variable de entorno TESTS
ENV TESTS="0"

# Entrypoint flexible: si TESTS=1 corre tests (forzando MOCK_ENGINE=1 para CI estable),
# si no ejecuta el modo interactivo real
ENTRYPOINT ["/bin/sh", "-c", "if [ \"$TESTS\" = '1' ]; then export MOCK_ENGINE=1; pytest tests/unit; else python -m src.cli; fi"]
