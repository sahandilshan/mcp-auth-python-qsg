# main.py
# This script has been rewritten to align with the latest mcp-auth documentation,
# using the recommended middleware pattern with Starlette and FastMCP.
#

import json
import uvicorn
from mcpauth.utils import fetch_server_config
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount

# Import the modern components from mcp and mcp-auth
from mcp.server.fastmcp import FastMCP
from mcpauth import MCPAuth, AuthInfo
from mcpauth.config import AuthServerType

# Import our custom JWT validator
from jwt_validator import create_jwt_validator

# --- Authentication and Server Configuration ---

# 1. Define authentication parameters - Asgardeo Configuration
# TODO: Replace 'your-tenant' with your actual Asgardeo tenant name
AUTH_ISSUER = "https://api.asgardeo.io/t/your-tenant/oauth2/token"
CLIENT_ID = "your-client-id-here"  # Replace with your Asgardeo OAuth2 client ID
JWKS_URL = "https://api.asgardeo.io/t/your-tenant/oauth2/jwks"

# Initialize JWT validator at startup
jwt_validator = create_jwt_validator(
    jwks_url=JWKS_URL,
    issuer=AUTH_ISSUER,
    audience=CLIENT_ID,
    ssl_verify=False  # Set to True for production
)

# 1. Define your resource identifier and fetch the config for its trusted authorization server.
auth_server_config = fetch_server_config(AUTH_ISSUER, AuthServerType.OIDC)

# 2. Configure the MCPAuth instance
# The MCPAuth object holds the configuration for all trusted authorization servers,
# keyed by the resource identifier they protect.
mcp_auth = MCPAuth(
    server=auth_server_config
)

# 3. Initialize the MCP Server using FastMCP
mcp = FastMCP(
    name='WhoAmI',
)

# --- Tool Definition ---

# 4. Define the 'whoami' tool
# It now accesses authentication details from the context variable `mcp_auth.auth_info`.
@mcp.tool('whoami')
async def whoami() -> dict:
    """A tool that returns the claims of the authenticated user."""
    try:
        # Access subject and claims directly from the auth info context
        sub = mcp_auth.auth_info.subject
        claims = mcp_auth.auth_info.claims

        # Log the subject for debugging
        print(f"Authenticated user subject: {sub}")

        if claims:
            claims_text = json.dumps(claims, indent=2)
            # The tool result should be a dictionary, which FastMCP will format
            return {"content": [{"type": "text", "text": claims_text}]}
        else:
            error_text = json.dumps({'error': 'No claims found in auth info'}, indent=2)
            return {"content": [{"type": "text", "text": error_text}]}

    except Exception as e:
        print(f"Error in whoami function: {e}")
        error_text = json.dumps({'error': 'Not authenticated'}, indent=2)
        return {"content": [{"type": "text", "text": error_text}]}

# --- Application Setup ---


def custom_verification(token: str) -> AuthInfo:
    """
    Custom JWT verification function that delegates to the JWT validator.
    """
    return jwt_validator.validate_token(token)

# 5. Create the Bearer authentication middleware
# This middleware protects our MCP server. It uses the custom verification function.
bearer_auth_middleware = mcp_auth.bearer_auth_middleware(
    custom_verification,
    # Specify the expected audience for the JWT for security.
    audience=CLIENT_ID,
    show_error_details=True
)

# 6. Create the Starlette web application
# We mount the MCP SSE application and protect it with the middleware.
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app(), middleware=[
            Middleware(bearer_auth_middleware)
        ])
    ]
)

# 7. Run the application
if __name__ == '__main__':
    # The server will listen on port 3001, same as the Node.js example.
    uvicorn.run(app, host='0.0.0.0', port=3001)
