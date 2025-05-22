
# image
FROM python:3.10-slim
# inside container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# reqs
COPY requirements.txt .

# libraries + dependencies 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
    
# project  & app files
COPY . .

# for streamlit
EXPOSE 8501 

# running the app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.enableCORS=false"]
