# MCP Auth Python Quick Start Guide - Asgardeo Integration

This project demonstrates how to create an authenticated MCP (Model Context Protocol) server using Python with Asgardeo as the OAuth2/OIDC provider.

## Features

- JWT token validation using JWKS (JSON Web Key Set)
- Asgardeo OAuth2/OIDC integration
- Custom JWT validator with SSL configuration
- MCP server with authentication middleware
- `whoami` tool that returns authenticated user's claims

## Prerequisites

- Python 3.12 or higher
- Asgardeo account and application setup
- pip (Python package installer)

## Project Structure

```
├── main.py              # Main MCP server application
├── jwt_validator.py     # JWT validation module
├── README.md           # This file
└── requirements.txt    # Python dependencies
```

## Installation

1. **Clone or download this project**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Asgardeo Configuration

### 1. Create an Asgardeo Application

1. Follow the https://wso2.com/asgardeo/docs/quick-starts/mcp-auth-server/#configure-an-application-in-asgardeo to create an application in Asgardeo.

### 2. Get Your Application Credentials

From your Asgardeo application, note down:
- **Client ID**: Found in the application's **Protocol** tab
- **Tenant Name**: Your organization's tenant name (visible in the URL)

### 3. Configure the Application

Edit `main.py` and update the following variables:

```python
# Replace 'your-tenant' with your actual Asgardeo tenant name
AUTH_ISSUER = "https://api.asgardeo.io/t/<your-tenant>/oauth2/token"
CLIENT_ID = "your-client-id-here"  # Replace with your Asgardeo OAuth2 client ID
JWKS_URL = "https://api.asgardeo.io/t/<your-tenant>/oauth2/jwks"
```

**Example with actual values:**
```python
AUTH_ISSUER = "https://api.asgardeo.io/t/mycompany/oauth2/token"
CLIENT_ID = "abc123xyz789_client_id_from_asgardeo"
JWKS_URL = "https://api.asgardeo.io/t/mycompany/oauth2/jwks"
```

## Running the Server

### Development Mode

1. **Start the server**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 3001 --reload
   ```

2. **Server will start on**: `http://localhost:3001`

### Production Mode

For production deployment:

1. **Update SSL settings** in `main.py`:
   ```python
   jwt_validator = create_jwt_validator(
       jwks_url=JWKS_URL,
       issuer=AUTH_ISSUER,
       audience=CLIENT_ID,
       ssl_verify=True  # Change to True for production
   )
   ```

2. **Run with production settings**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 3001 --workers 4
   ```

## Testing the Server

### 1. Get an Access Token from Asgardeo

You can obtain an access token using various OAuth2 flows. For testing, you can use:

**Client Credentials Flow (for machine-to-machine):**
```bash
curl -X POST "https://api.asgardeo.io/t/your-tenant/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=your-client-id&client_secret=your-client-secret"
```

**Authorization Code Flow (for user authentication):**
1. Direct users to the authorization URL
2. Handle the callback to get the authorization code
3. Exchange the code for an access token

### 2. Test the MCP Server

Once you have an access token, you can test the server by making authenticated requests with the Bearer token in the Authorization header.

The server provides a `whoami` tool that returns the authenticated user's JWT claims.

## Configuration Options

### SSL Verification

- **Development**: Set `ssl_verify=False` for local testing with self-signed certificates
- **Production**: Set `ssl_verify=True` for proper SSL certificate validation

### JWT Validation Settings

The JWT validator supports the following algorithms and validations:
- **Algorithm**: RS256 (configurable)
- **Expiration**: Verified
- **Audience**: Verified against CLIENT_ID
- **Issuer**: Verified against AUTH_ISSUER

## Troubleshooting

### Common Issues

1. **SSL Certificate Error**
   - Ensure `ssl_verify=False` for development
   - For production, ensure proper SSL certificates

2. **Token Validation Failed**
   - Verify your CLIENT_ID matches the audience in the JWT
   - Ensure AUTH_ISSUER matches the issuer in the JWT
   - Check that your Asgardeo tenant name is correct

3. **JWKS Fetch Error**
   - Verify the JWKS_URL is accessible
   - Check network connectivity to Asgardeo

### Debug Mode

Enable debug logging by adding print statements or using Python's logging module:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Security Considerations

- Always use HTTPS in production
- Set `ssl_verify=True` for production environments
- Regularly rotate your client secrets
- Monitor token validation failures
- Implement proper error handling and logging

## API Endpoints

- **MCP Tools**: Accessible via MCP protocol with proper authentication
- **whoami Tool**: Returns authenticated user's JWT claims


For issues related to:
- **Asgardeo**: Check [Asgardeo Documentation](https://wso2.com/asgardeo/docs/)
- **MCP Framework**: Check MCP documentation
- **This Implementation**: Review the code comments and error messages
