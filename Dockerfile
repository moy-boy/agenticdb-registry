# Use the official Python 3.12.5 image with Debian Bookworm
FROM python:3.12.5-bookworm

# Set the working directory
WORKDIR /app/app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Python dependencies if you have a requirements.txt file
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy your application code to the container
COPY . /app

# Expose port 8000 for the application
EXPOSE 8000

# Command to run your application
CMD ["python", "server.py"]
