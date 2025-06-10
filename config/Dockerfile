# Use Python 3.11 as the base image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /app

# Copy project files to the container
COPY . /app

# Install required dependencies
RUN pip install fastapi uvicorn pandas joblib scikit-learn

# Expose the FastAPI port
EXPOSE 8000

# Command to start the API
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
