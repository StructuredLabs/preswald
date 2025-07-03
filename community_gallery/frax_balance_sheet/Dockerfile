FROM python:3.12-slim

WORKDIR /app

# Install Node.js and npm (required by Preswald)
RUN apt-get update && apt-get install -y nodejs npm

# Copy project files
COPY pyproject.toml .
COPY preswald.toml .
COPY hello.py .
COPY data/ data/

# Install dependencies
RUN pip install preswald==0.1.42
RUN pip install setuptools

# Run the app
CMD ["preswald", "run"]

# Expose port 8501
EXPOSE 8501
