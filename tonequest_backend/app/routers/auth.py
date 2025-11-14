from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin.auth import InvalidIdTokenError, ExpiredIdTokenError, UserRecord
from google.cloud.firestore import Client
import requests
import json

# Import the pre-initialized auth module from your firebase_config
from app.firebase_config import firebase_auth, get_firebase_web_config
from app.dependencies import get_db
from app.schemas import User, UserSignup, UserLogin, AuthResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

# This tells FastAPI to look for an 'Authorization: Bearer <token>' header.
security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    A FastAPI dependency that verifies the Firebase ID token
    and returns the user's decoded token (payload).
    
    If the token is invalid or expired, it raises an HTTPException.
    """
    try:
        if credentials is None or not getattr(credentials, "credentials", None):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization credentials missing",
                headers={"WWW-Authenticate": "Bearer"},
            )
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


@router.post("/signup", response_model=AuthResponse)
def signup(user_data: UserSignup, db: Client = Depends(get_db)):
    """
    Create a new user with Firebase Auth and store profile in Firestore.
    """
    try:
        # Create user in Firebase Auth
        user_record: UserRecord = firebase_auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.displayName
        )
        
        # Create custom token for immediate login
        custom_token = firebase_auth.create_custom_token(user_record.uid)
        
        # Exchange custom token for ID token using Firebase REST API
        firebase_config = get_firebase_web_config()
        api_key = firebase_config.get("apiKey")
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase API key not configured"
            )
        
        # Exchange custom token for ID token
        token_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={api_key}"
        token_response = requests.post(token_url, json={
            "token": custom_token.decode(),
            "returnSecureToken": True
        })
        
        if token_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate authentication token"
            )
        
        token_data = token_response.json()
        id_token = token_data["idToken"]
        
        # Create user document in Firestore
        user_doc = {
            "uid": user_record.uid,
            "email": user_data.email,
            "displayName": user_data.displayName or "",
            "totalSubmissions": 0,
            "answeredQuestionIds": []
        }
        
        user_ref = db.collection("users").document(user_record.uid)
        user_ref.set(user_doc)
        
        return AuthResponse(
            user=User(**user_doc),
            token=id_token,
            message="User created successfully"
        )
        
    except firebase_auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
def login(user_data: UserLogin, db: Client = Depends(get_db)):
    """
    Authenticate user with email/password and return user data with token.
    """
    try:
        # Get Firebase config
        firebase_config = get_firebase_web_config()
        api_key = firebase_config.get("apiKey")
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase API key not configured"
            )
        
        # Authenticate with Firebase REST API
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        auth_response = requests.post(auth_url, json={
            "email": user_data.email,
            "password": user_data.password,
            "returnSecureToken": True
        })
        
        if auth_response.status_code != 200:
            error_data = auth_response.json()
            error_message = error_data.get("error", {}).get("message", "Invalid credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {error_message}"
            )
        
        auth_data = auth_response.json()
        uid = auth_data["localId"]
        id_token = auth_data["idToken"]
        
        # Get user from Firestore
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Please contact support."
            )
        
        user_data = user_doc.to_dict() or {}
        return AuthResponse(
            user=User(**user_data),
            token=id_token,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=User)
def get_current_user_profile(current_user: dict = Depends(get_current_user), db: Client = Depends(get_db)):
    """
    Get current user's profile information.
    """
    uid = current_user["uid"]
    
    user_ref = db.collection("users").document(uid)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return User(**user_doc.to_dict())