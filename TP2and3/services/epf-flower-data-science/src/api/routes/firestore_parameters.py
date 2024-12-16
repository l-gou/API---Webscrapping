from fastapi import APIRouter, HTTPException, Request
from google.cloud import firestore
from typing import Dict, Union, List
from pydantic import BaseModel
from google.oauth2 import service_account
import google.auth
from firebase_admin import auth

# Initialisation de l'API router
router = APIRouter()

# Initialiser Firestore
credentials = service_account.Credentials.from_service_account_file( 'TP2and3/careful-maxim-443609-j6-bbedea89fd10.json'  )
db = firestore.Client(credentials=credentials)


class Parameters(BaseModel):
    """Modèle Pydantic pour valider les paramètres."""
    n_estimators: int
    criterion: str

class ParamUpdate(BaseModel):
    """Pydantic model for updating parameters."""
    n_estimators: int
    criterion: str


class ParametersResponse(BaseModel):
    """Response model for adding or updating parameters."""
    message: str
    parameters: dict

class UserRegisterRequest(BaseModel):
    """Pydantic model for user registration."""
    email: str
    password: str



@router.get("/parameters")
async def get_parameters() -> Dict[str, Union[Dict[str, str], str]]:
    """
    Retrieve all parameters from the Firestore "parameters" collection.

    Returns:
        A dictionary of parameters from the Firestore collection or an error message in case of failure.
    
    Example:
        {
            "param_1": {"n_estimators": 100, "criterion": "gini"},
            "param_2": {"n_estimators": 200, "criterion": "entropy"}
        }
    """
    try:
        # Retrieve all documents from the "parameters" collection
        docs = db.collection("parameters").stream()

        # Prepare the response data in a dictionary format
        parameters = {}
        for doc in docs:
            parameters[doc.id] = doc.to_dict()

        return parameters
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching parameters: {e}")


@router.post("/parameters", response_model=ParametersResponse)
async def add_or_update_parameters(parameters: Parameters) -> ParametersResponse:
    """
    Add or update parameters in Firestore.

    Args:
        parameters: The parameters to be added or updated.

    Returns:
        A response model containing a success message and the parameters.

    Raises:
        HTTPException: If an error occurs while interacting with Firestore.
    """
    try:
        doc_ref = db.collection("parameters").document("parameters")
        doc = doc_ref.get()

        # Si le document existe déjà, récupérez les paramètres existants
        if doc.exists:
            existing_params = doc.to_dict()
            param_num = len(existing_params) + 1
            param_key = f"param_{param_num}"
            existing_params[param_key] = parameters.dict()  # Ajouter le nouveau paramètre
            doc_ref.set(existing_params)  # Mettre à jour le document
        else:
            # Si le document n'existe pas, créez-le avec le premier paramètre
            doc_ref.set({f"param_1": parameters.dict()})

        return ParametersResponse(message="Paramètre ajouté avec succès", parameters=parameters.dict())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Une erreur s'est produite : {str(e)}")


def clear_collection(collection_name: str) -> None:
    """
    Clear all documents from a Firestore collection.

    Args:
        collection_name: The name of the collection to be cleared.

    Returns:
        None

    Raises:
        None: Just deletes documents from the specified collection.
    """
    # Récupérer tous les documents dans la collection
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()

    # Supprimer chaque document
    for doc in docs:
        doc.reference.delete()
        print(f"Document {doc.id} supprimé.")

# Appeler la fonction pour effacer tous les documents dans la collection 'parameters'
#clear_collection('parameters')


@router.post("/parameters/{param_id}")
async def update_parameter(param_id: str, param: ParamUpdate) -> Dict[str, str]:
    """
    Update parameters in Firestore based on param_id.

    Args:
        param_id: The ID of the parameter to be updated.
        param: The updated parameter values.

    Returns:
        A message confirming the update.
    
    Raises:
        HTTPException: If an error occurs while updating the parameter.
    """
    try:
        doc_ref = db.collection("parameters").document(param_id)
        
        # Log the parameters that will be updated
        print(f"Updating parameter {param_id} with: {param.dict()}")
        
        # Met à jour le document avec les nouveaux paramètres
        doc_ref.set({
            "n_estimators": param.n_estimators,
            "criterion": param.criterion
        })
        
        return {"message": f"Paramètre {param_id} mis à jour avec succès."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour : {e}")




############## Step 16 ################


def verify_token(token: str) -> dict:
    """
    Verify the ID token using Firebase Authentication.

    Args:
        token: The Firebase ID token to verify.

    Returns:
        A dictionary with the decoded user information.

    Raises:
        HTTPException: If the token is invalid.
    """
    try:
        # Verify the token with Firebase Authentication
        decoded_token = auth.verify_id_token(token)
        return decoded_token  # Contains user information
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized. Invalid token.")

def get_current_user(request: Request) -> dict:
    """
    Get the current user from the request by extracting and verifying the token.

    Args:
        request: The FastAPI Request object.

    Returns:
        A dictionary with the user information.

    Raises:
        HTTPException: If the authorization token is missing or invalid.
    """
    # Extract token from Authorization header
    authorization_header = request.headers.get("Authorization")
    if not authorization_header:
        raise HTTPException(status_code=401, detail="Authorization token missing")
    
    # The token is usually in the form "Bearer <token>"
    token = authorization_header.split(" ")[1]
    print(token)
    # Verify the token
    user = verify_token(token)
    print(user)

    return user

############## Step 17 ################

import firebase_admin

from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import auth

router = APIRouter()

credentials = service_account.Credentials.from_service_account_file( 'TP2and3/careful-maxim-443609-j6-bbedea89fd10.json'  )


firebase_admin.initialize_app(credentials)

from fastapi import Query

@router.post("/register")

async def register_user(email: str, password: str) -> dict:
    """
    Register a new user using Firebase Authentication.

    Args:
        email: The email of the user.
        password: The password of the user.

    Returns:
        A dictionary containing the registration success message.

    Raises:
        HTTPException: If there is an error during registration.
    """
    try:
        # Create user with email and password
        new_user = auth.create_user(
            email=email,
            password=password,
        )
        return {"message": f"User {new_user.uid} created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error registering user: {e}")



@router.post("/login")
async def login_user(id_token: str) -> dict:
    """
    Login a user using Firebase Authentication and ID token.

    Args:
        id_token: The Firebase ID token for the user.

    Returns:
        A dictionary containing the login success message and user info.

    Raises:
        HTTPException: If the ID token is invalid.
    """
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        return {"message": "User logged in successfully", "user_info": decoded_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID token")



@router.post("/logout")
async def logout_user(id_token: str) -> dict:
    """
    Log out the user by revoking their refresh token.

    Args:
        id_token: The Firebase ID token of the user to log out.

    Returns:
        A dictionary containing the logout success message.

    Raises:
        HTTPException: If there is an error during logout.
    """
    try:
        # Revoke the refresh token for the current user (force logout)
        decoded_token = auth.verify_id_token(id_token)
        auth.revoke_refresh_tokens(decoded_token["uid"])
        return {"message": "User logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error logging out user")



def assign_admin_role(user_uid: str) -> None:
    """
    Assign the 'admin' role to a user by setting custom claims in Firebase.

    Args:
        user_uid: The UID of the user to be assigned the 'admin' role.

    Returns:
        None
    
    Raises:
        Exception: If there is an error assigning the role.
    """
    try:
        auth.set_custom_user_claims(user_uid, {"role": "admin"})
    except Exception as e:
        print(f"Error assigning role: {e}")



def get_user_role(id_token: str) -> str:
    """
    Get the role of a user by verifying their Firebase ID token.

    Args:
        id_token: The Firebase ID token to verify.

    Returns:
        The user's role (default is "user" if no custom role is set).
    
    Raises:
        HTTPException: If there is an error fetching the role.
    """
    try:
        decoded_token = auth.verify_id_token(id_token)
        role = decoded_token.get("role", "user")  # Default role is "user"
        return role
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching user role")


@router.get("/users")
async def get_all_users(request: Request, current_user: dict = Depends(get_current_user)) -> dict:
    """
    Get all users from Firestore (admins only).

    Args:
        request: The FastAPI Request object.
        current_user: The currently authenticated user.

    Returns:
        A dictionary containing all users.

    Raises:
        HTTPException: If the user is not an admin.
    """
    role = get_user_role(current_user["uid"])
    if role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden. Admins only.")
    
    # Fetch all users from Firestore (or another service)
    users = db.collection("users").stream()
    users_list = [user.to_dict() for user in users]
    
    return {"users": users_list}
