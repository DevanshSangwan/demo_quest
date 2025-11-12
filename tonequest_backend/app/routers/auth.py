from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin.auth import InvalidIdTokenError, ExpiredIdTokenError

# Import the pre-initialized auth module from your firebase_config
from app.firebase_config import firebase_auth 

# This tells FastAPI to look for an 'Authorization: Bearer <token>' header.
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    A FastAPI dependency that verifies the Firebase ID token
    and returns the user's decoded token (payload).
    
    If the token is invalid or expired, it raises an HTTPException.
    """
    try:
        # Extract the token from the credentials
        token = credentials.credentials
        # Verify the token against the Firebase Auth API
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
        
    except ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidIdTokenError:
        # This handles tokens that are malformed, have the wrong signature, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Handle other potential errors (e.g., Firebase network issues)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verifying token: {e}",
        )