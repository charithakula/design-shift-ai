# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code into the container
COPY . .

# Expose port for Streamlit (default 8501)
EXPOSE 8501

# Set environment variable to prevent .pyc files creation and enable stdout/stderr buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Command to run your app - adjust as needed
CMD ["streamlit", "run", "ui/web_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
