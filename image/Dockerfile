# Development Dockerfile - much faster to build
FROM public.ecr.aws/lambda/python:3.11

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Local Testing  
EXPOSE 8000

# Set Environment Variable 
ENV IS_USING_IMAGE_RUNTIME=True
ENV PYTHONPATH=/app

# Copy the entire src directory
COPY src/ /app/

# For Lambda compatibility, we still provide the handler
# But also support direct Python execution
CMD ["python", "main.py"]
