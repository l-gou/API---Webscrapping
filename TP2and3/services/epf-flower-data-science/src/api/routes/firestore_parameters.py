from fastapi import APIRouter, HTTPException
from google.cloud import firestore
from pydantic import BaseModel
from google.oauth2 import service_account
import google.auth

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

