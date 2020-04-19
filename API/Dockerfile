# Use an official Python runtime as a parent image
FROM python:3.7

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./


# COPY requirements.txt /tmp
# WORKDIR /tmp
# Install any needed packages
RUN pip3 install -r requirements.txt

# COPY src/ app/

# Set the working directory to /app
# WORKDIR /app

# Copy the current directory contents into the container at /app
# COPY . /app




# Make port 8080 available
ENV PORT 5000

# CMD python flask_wep_app.py
CMD ["python", "flask_wep_app.py"]