"""
JWT Token Validation Module

This module handles JWT token validation using JWKS (JSON Web Key Set).
It provides a clean interface for validating JWT tokens with proper error handling.
"""

import jwt
import ssl
from typing import Dict, Any, Optional
from jwt import PyJWKClient
from mcpauth import AuthInfo


class JWTValidator:
    """
    A class to handle JWT token validation using JWKS.
    Initializes JWKS client at startup and caches keys for performance.
    """

    def __init__(self, jwks_url: str, issuer: str, audience: str, ssl_verify: bool = True):
        """
        Initialize the JWT validator.

        Args:
            jwks_url: The URL to fetch JWKS from
            issuer: Expected token issuer
            audience: Expected token audience
            ssl_verify: Whether to verify SSL certificates (False for dev/testing)
        """
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.audience = audience
        self.jwks_client: Optional[PyJWKClient] = None

        # Initialize JWKS client
        self._initialize_jwks_client(ssl_verify)

    def _initialize_jwks_client(self, ssl_verify: bool) -> None:
        """Initialize the JWKS client with appropriate SSL settings."""
        try:
            if not ssl_verify:
                # Create SSL context for development/testing
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE

                self.jwks_client = PyJWKClient(
                    self.jwks_url,
                    ssl_context=ssl_context
                )
            else:
                # Production configuration with SSL verification
                self.jwks_client = PyJWKClient(self.jwks_url)

            print(f"JWKS client initialized for {self.jwks_url}")

        except Exception as e:
            print(f"Warning: Failed to initialize JWKS client: {e}")
            raise

    def validate_token(self, token: str) -> AuthInfo:
        """
        Validate a JWT token and return AuthInfo.

        Args:
            token: The JWT token to validate

        Returns:
            AuthInfo: Validated token information

        Raises:
            ValueError: If token validation fails
        """
        if self.jwks_client is None:
            raise ValueError("JWKS client not initialized")

        try:
            # Get the signing key from JWKS
            signing_key = self.jwks_client.get_signing_key_from_jwt(token)

            # Decode and validate the JWT
            decoded_token = jwt.decode(
                token,
                signing_key.key,
                algorithms=["RS256"],  # Can be made configurable if needed
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "verify_exp": True,
                    "verify_aud": True,
                    "verify_iss": True
                }
            )

            # Extract claims
            subject = decoded_token.get("sub")
            audience = decoded_token.get("aud")

            # Return AuthInfo with proper claims
            return AuthInfo(
                token=token,
                claims=decoded_token,
                issuer=self.issuer,
                subject=subject,
                audience=audience
            )

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidAudienceError:
            raise ValueError("Invalid audience")
        except jwt.InvalidIssuerError:
            raise ValueError("Invalid issuer")
        except jwt.InvalidSignatureError:
            raise ValueError("Invalid token signature")
        except jwt.DecodeError:
            raise ValueError("Invalid token format")
        except Exception as e:
            raise ValueError(f"Token validation failed: {str(e)}")


def create_jwt_validator(jwks_url: str, issuer: str, audience: str, ssl_verify: bool = True) -> JWTValidator:
    """
    Factory function to create a JWT validator instance.

    Args:
        jwks_url: The URL to fetch JWKS from
        issuer: Expected token issuer
        audience: Expected token audience
        ssl_verify: Whether to verify SSL certificates

    Returns:
        JWTValidator: Configured validator instance
    """
    return JWTValidator(jwks_url, issuer, audience, ssl_verify)
