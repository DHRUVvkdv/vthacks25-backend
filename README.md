# VTHacks 2025 Backend

A super simple FastAPI application with API key authentication - perfect for hackathons!

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Simple Authentication**: Single API key from environment variable
- **CORS Enabled**: Full CORS support for web applications
- **AWS Lambda Ready**: Deploy to AWS Lambda with Mangum adapter
- **Interactive Docs**: Swagger UI with API key authorization
- **Minimal Dependencies**: Only 4 packages needed

## Quick Start

### Prerequisites

- Python 3.9+
- Virtual environment (venv)

### Setup

1. **Clone and navigate to the project**

   ```bash
   cd vthacks25-backend
   ```

2. **Create and activate virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r image/requirements.txt
   ```

4. **Set up your API key**

   ```bash
   cd image/src
   echo 'API_KEY=your_secret_key_here' > .env
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

### API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

#### Public Endpoints (No Authentication)

- `GET /` - Welcome message
- `GET /health` - Health check

#### Protected Endpoints (Require API Key)

- `GET /protected` - Simple protected endpoint
- `GET /api/data` - Sample data endpoint

### Authentication

This API uses **simple API key authentication** from your `.env` file.

#### Setup Your API Key

1. **Configure**: Set `API_KEY=your_key` in `image/src/.env`
2. **Use**: Include as `X-API-Key` header in requests

#### API Key Usage

```bash
# Public endpoints (no auth needed)
curl http://localhost:8000/
curl http://localhost:8000/health

# Protected endpoints (API key required)
curl -H "X-API-Key: your_key" http://localhost:8000/protected
curl -H "X-API-Key: your_key" http://localhost:8000/api/data
```

#### Interactive API Documentation

Visit http://localhost:8000/docs to use the Swagger UI:

1. Click the **"Authorize"** button (🔒 icon)
2. Enter your API key from `.env` file
3. Click **"Authorize"**
4. Test all endpoints directly in the browser!

### CORS Support

Full CORS support is enabled for all origins, methods, and headers - perfect for web applications!

## Project Structure

**Super simple structure - everything you need in minimal files:**

```
vthacks25-backend/
├── README.md              # This file
├── .gitignore             # Git ignore rules
├── venv/                  # Virtual environment
└── image/                 # Application files
    ├── Dockerfile         # For AWS Lambda deployment
    ├── requirements.txt   # Just 4 dependencies!
    └── src/
        ├── main.py        # Complete FastAPI app (57 lines)
        └── .env           # Your API key: API_KEY=your_key
```

## Dependencies

Only 4 packages needed:

- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `mangum` - AWS Lambda adapter
- `python-dotenv` - Environment variables

## Docker Deployment

```bash
# Build for AWS Lambda
cd image
docker build -t vthacks25-backend .

# Run locally with Docker
docker run -p 8000:8000 --env-file src/.env vthacks25-backend
```

## AWS CLI Setup

### Prerequisites

- AWS account with access credentials
- No admin privileges required on local machine

### Installation & Configuration

```bash
# Download and install AWS CLI v2 (user-space installation)
curl "https://awscli.amazonaws.com/awscli-exe-macos.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install --install-dir ~/aws-cli --bin-dir ~/aws-cli/bin

# Add to PATH
echo 'export PATH=$HOME/aws-cli/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

# Configure AWS profile
aws2 configure --profile dv-per
# Enter: Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)

# Disable SSL verification if needed (corporate networks)
aws2 configure set ca_bundle "" --profile dv-per

# Test connection
aws2 s3 ls --profile dv-per
```

## AWS Lambda Deployment

This application is configured for AWS Lambda deployment using:

- **Mangum**: ASGI adapter for Lambda
- **AWS Lambda Python Runtime**: Public ECR base image
- **Handler**: `main.handler` (configured in Dockerfile)

The same codebase works for both local development and Lambda deployment.

# how to run:

docker build -t vt25 .  
docker run -p 8000:8000 --env-file .env --entrypoint "" vt25 python main.py
