
# Use an official Python runtime as base image
FROM python:3.8-slim-buster

# Set environment variables
ENV DISCORD_BOT_TOKEN=your_discord_bot_token
ENV OPENAI_API_KEY=your_openai_api_key

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "./run.py"]
