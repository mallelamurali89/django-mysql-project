# Use an official Python runtime as a parent image
FROM python:3.10.7

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create and set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port your application runs on
EXPOSE 8000

# Run Django migrations
RUN python manage.py migrate

# Define the command to run your application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
