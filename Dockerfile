
# image
FROM python:3.10-slim
# inside container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
# reqs
COPY requirements.txt .

# libraries + depend
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/* 
    
# project 
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .

# for streamlit
EXPOSE 8501 
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.enableCORS=false"]
