from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from app.core.config import settings

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the Bearer token against Clerk's public key.
    In a real production app, you might want to cache the JWKS or use the Clerk SDK directly if available and preferred.
    For this scaffold, we'll assume the PEM key is provided in env vars or a simplified validation.
    """
    token = credentials.credentials
    
    try:
        # Verify the token using the public key provided by Clerk (PEM format)
        # Note: In production you should fetch JWKS from Clerk /.well-known/jwks.json
        # Here we assume CLERK_PEM_PUBLIC_KEY is set in env for simplicity or use a flexible decoding if just testing
        


        # DEBUG: Print key info to debug the issue
        key_len = len(settings.CLERK_PEM_PUBLIC_KEY) if settings.CLERK_PEM_PUBLIC_KEY else 0
        print(f"DEBUG: Key length: {key_len}")
        print(f"DEBUG: Key start: {settings.CLERK_PEM_PUBLIC_KEY[:20] if settings.CLERK_PEM_PUBLIC_KEY else 'None'}")
        

        # Check if key is the default placeholder, empty, or a Publishable Key (pk_...) mistakenly used
        is_placeholder = settings.CLERK_PEM_PUBLIC_KEY == "your_clerk_pem_public_key"
        is_publishable_key = settings.CLERK_PEM_PUBLIC_KEY.startswith("pk_")
        
        if not settings.CLERK_PEM_PUBLIC_KEY or is_placeholder or is_publishable_key:
             # Just decode without verification for dev if no key (NOT SECURE)
             if is_publishable_key:
                 print("WARNING: You provided a Clerk Publishable Key (pk_...) instead of a PEM Public Key.")
                 print("WARNING: Skipping signature verification for DEV mode.")
             else:
                 print(f"WARNING: Skipping signature verification. Key configured: {not is_placeholder}")
                 
             payload = jwt.decode(token, options={"verify_signature": False})
        else:
            payload = jwt.decode(token, settings.CLERK_PEM_PUBLIC_KEY, algorithms=["RS256"])
            
        return payload
    except jwt.PyJWTError as e:
        print(f"JWT Validation Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
