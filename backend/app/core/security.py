"""
Security utilities for Supabase JWT verification.
"""
import json
import time
import logging
from typing import Dict, Optional

import httpx
from jose import jwt, jwk
from jose.exceptions import JOSEError, JWTError

from app.core.config import settings

logger = logging.getLogger(__name__)

# Cache for JWKS with timestamp
_jwks_cache: dict = {"keys": None, "timestamp": 0}
_JWKS_CACHE_TTL = 300  # 5 minutes


def get_jwks() -> dict:
    """
    Fetch and cache Supabase JSON Web Key Set (JWKS).

    Returns:
        dict: JWKS data containing public keys for token verification

    Raises:
        RuntimeError: If unable to fetch JWKS from Supabase
        ValueError: If Supabase URL is not configured
    """
    global _jwks_cache

    # Return cached version if still valid
    now = time.time()
    if _jwks_cache["keys"] is not None and (now - _jwks_cache["timestamp"]) < _JWKS_CACHE_TTL:
        logger.debug("Returning cached JWKS")
        return _jwks_cache["keys"]

    # Check if Supabase is configured
    if not settings.SUPABASE_URL:
        raise ValueError("SUPABASE_URL is not configured")

    # Determine JWKS URL
    jwks_url = getattr(settings, 'SUPABASE_JWKS_URL', None)
    if not jwks_url:
        # Construct URL from SUPABASE_URL
        supabase_url = str(settings.SUPABASE_URL).rstrip('/')
        jwks_url = f"{supabase_url}/auth/v1/keys"

    try:
        logger.debug(f"Fetching JWKS from {jwks_url}")
        response = httpx.get(jwks_url, timeout=10.0)
        response.raise_for_status()
        jwks = response.json()

        # Update cache
        _jwks_cache["keys"] = jwks
        _jwks_cache["timestamp"] = now
        logger.info("Successfully fetched and cached JWKS")

        return jwks
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        # Network or HTTP error
        logger.warning(f"Failed to fetch JWKS from {jwks_url}: {e}")
        # If we have cached data (even if expired), use it as fallback
        if _jwks_cache["keys"] is not None:
            logger.info("Using expired JWKS cache due to fetch failure")
            return _jwks_cache["keys"]
        raise RuntimeError(f"Failed to fetch JWKS from {jwks_url}: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON response from JWKS endpoint {jwks_url}: {e}")
        # If we have cached data (even if expired), use it as fallback
        if _jwks_cache["keys"] is not None:
            logger.info("Using expired JWKS cache due to invalid JSON")
            return _jwks_cache["keys"]
        raise RuntimeError(f"Invalid JSON response from JWKS endpoint {jwks_url}: {str(e)}")


def verify_supabase_jwt(token: str) -> Optional[dict]:
    """
    Verify a Supabase JWT token.

    Args:
        token: The JWT token to verify (may include 'Bearer ' prefix)

    Returns:
        dict: Decoded token payload if valid, None if invalid
    """
    # Remove 'Bearer ' prefix if present
    if token.startswith('Bearer '):
        token = token[7:]

    try:
        # Get unverified header to get key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        if not kid:
            logger.warning("Token missing 'kid' header")
            return None

        # Get JWKS and find the matching key
        jwks = get_jwks()
        key_dict = None

        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                key_dict = key
                break

        if not key_dict:
            logger.warning(f"No matching key found for kid='{kid}'")
            return None

        # Construct public key from JWK
        public_key = jwk.construct(key_dict)

        # Verify the token
        payload = jwt.decode(
            token,
            public_key.to_pem().decode('utf-8'),
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            options={"verify_signature": True, "verify_exp": True, "verify_aud": True}
        )

        logger.debug(f"Successfully verified token for user {payload.get('sub')}")
        return payload

    except (JWTError, JOSEError, KeyError, AttributeError, ValueError) as e:
        # Token is invalid for any reason; log at debug level to avoid leaking info
        logger.debug(f"Token verification failed: {e}")
        return None