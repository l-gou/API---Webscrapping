from fastapi import APIRouter, HTTPException, Request
from google.cloud import firestore
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
    n_estimators: int
    criterion: str


class ParametersResponse(BaseModel):
    message: str
    parameters: dict

class UserRegisterRequest(BaseModel):
    email: str
    password: str



@router.get("/parameters")
async def get_parameters():
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
async def add_or_update_parameters(parameters: Parameters):
    """Ajouter ou mettre à jour des paramètres dans Firestore."""
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


def clear_collection(collection_name):
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
async def update_parameter(param_id: str, param: ParamUpdate):
    """
    Met à jour les paramètres dans Firestore en fonction de param_id
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


def verify_token(token: str):
    try:
        # Verify the token with Firebase Authentication
        decoded_token = auth.verify_id_token(token)
        return decoded_token  # Contains user information
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized. Invalid token.")

def get_current_user(request: Request):
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

async def register_user(email: str = Query(...), password: str = Query(...)):
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
async def login_user(id_token: str):
    try:
        # Verify the ID token
        decoded_token = auth.verify_id_token(id_token)
        return {"message": "User logged in successfully", "user_info": decoded_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid ID token")



@router.post("/logout")
async def logout_user(id_token: str):
    try:
        # Revoke the refresh token for the current user (force logout)
        decoded_token = auth.verify_id_token(id_token)
        auth.revoke_refresh_tokens(decoded_token["uid"])
        return {"message": "User logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error logging out user")



def assign_admin_role(user_uid: str):
    try:
        auth.set_custom_user_claims(user_uid, {"role": "admin"})
    except Exception as e:
        print(f"Error assigning role: {e}")



def get_user_role(id_token: str):
    try:
        decoded_token = auth.verify_id_token(id_token)
        role = decoded_token.get("role", "user")  # Default role is "user"
        return role
    except Exception as e:
        raise HTTPException(status_code=400, detail="Error fetching user role")


@router.get("/users")
async def get_all_users(request: Request, current_user: dict = Depends(get_current_user)):
    role = get_user_role(current_user["uid"])
    if role != "admin":
        raise HTTPException(status_code=403, detail="Forbidden. Admins only.")
    
    # Fetch all users from Firestore (or another service)
    users = db.collection("users").stream()
    users_list = [user.to_dict() for user in users]
    
    return {"users": users_list}
