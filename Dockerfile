
# image
FROM python:3.10-slim
# inside container
WORKDIR /app
# reqs
COPY requirements.txt .

# libraries + depend
RUN apt-get update && apt-get install -y \
    build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean
# project - > container
COPY . .

# for streamlit
EXPOSE 8501 
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
