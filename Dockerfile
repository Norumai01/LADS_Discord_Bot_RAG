FROM python:3.11-slim
LABEL authors="norumai"

# Set working directory
WORKDIR /app

# System dependencies and updates
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements_bot.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements_bot.txt

# Bake in the embedding model + nltk corpus at build time so the container
# doesn't need internet access to fetch them on first run.
ENV HF_HOME=/app/.cache/huggingface
ENV NLTK_DATA=/app/.cache/nltk_data
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-small-en-v1.5')" && \
    python -c "import nltk; nltk.download('stopwords', download_dir='/app/.cache/nltk_data')"

# Copy the application code (changes most often, so it stays in its own layer)
COPY . .

CMD ["python", "main_sylus.py"]
