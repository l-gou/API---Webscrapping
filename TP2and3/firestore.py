import google.auth
from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials, auth



class FirestoreClient:
    """Wrapper around a database"""

    client: firestore.Client

    def __init__(self) -> None:
        """Init the client."""
        credentials, _ = google.auth.default()

        self.client = firestore.Client(credentials=credentials)

    def get(self, collection_name: str, document_id: str) -> dict:
        """Find one document by ID.
        Args:
            collection_name: The collection name
            document_id: The document id
        Return:
            Document value.
        """
        doc = self.client.collection(
            collection_name).document(document_id).get()
        if doc.exists:
            return doc.to_dict()
        raise FileExistsError(
            f"No document found at {collection_name} with the id {document_id}"
        )

########## Step 13: Create Firestore Collection with Parameters #############

    def create_parameters_document(self, n_estimators: int, criterion: str) -> str:
        """Create the 'parameters' document in the 'parameters' collection.

        Args:
            n_estimators (int): The number of estimators parameter.
            criterion (str): The criterion parameter.
        
        Returns:
            str: A message indicating whether the document was successfully created.
        """
        # Define the data to be written
        parameters_data = {
            'n_estimators': n_estimators,
            'criterion': criterion
        }

        # Create the collection and document
        try:
            self.client.collection('parameters').document('parameters').set(parameters_data)
            return "Document 'parameters' created successfully in 'parameters' collection."
        except Exception as e:
            return f"Error creating document: {e}"

########## Step 14: Retrieve Parameters from Firestore #############

    def get_parameters(self) -> dict:
        """Retrieve the parameters document."""
        return self.get("parameters", "parameters")


########## Step 15: Update or Add Parameters in Firestore #############

    def update_or_add_parameters(self, n_estimators: int, criterion: str) -> None:
            """Update or add parameters in Firestore."""
            data = {
                "n_estimators": n_estimators,
                "criterion": criterion
            }
            self.client.collection("parameters").document("parameters").set(data)



########## Step 16: Authentication with Firestore ##########


class FirestoreClient:
    def __init__(self) -> None:
        """Init the client and Firebase Admin."""
        credentials, _ = google.auth.default()
        self.client = firestore.Client(credentials=credentials)
        
        # Initialize Firebase Admin SDK with your service account
        firebase_cred = credentials.Certificate("path/to/serviceAccountKey.json")
        firebase_admin.initialize_app(firebase_cred)

    def authenticate_user(self, id_token: str) -> dict:
        """Authenticate a user with Firebase Auth."""
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token

########## Step 17: User Management (Registration, Login, Logout, Roles) ##########



    def register_user(self, email: str, password: str) -> dict:
        """Register a new user."""
        user = auth.create_user(
            email=email,
            password=password,
        )
        return user

    def login_user(self, email: str, password: str) -> dict:
        """Login an existing user and return their token."""
        # Firebase doesn't directly provide a login function via SDK. 
        # You'd need to use Firebase Authentication REST API for login here or 
        # implement a client-side login flow in a web/mobile app.
        pass
    
    def assign_user_role(self, uid: str, role: str) -> None:
        """Assign a role to a user (e.g., 'admin')."""
        auth.set_custom_user_claims(uid, {'role': role})

    def logout_user(self) -> None:
        """Log out a user."""
        # Firebase handles token expiration and revocation for you, but you can clear client-side tokens.
        pass



##########    Step 18: Protection Against Denial of Service (DoS) Attacks with Rate Limiting ##########

import time
class RateLimiter:
    def __init__(self, max_requests: int, window_sec: int) -> None:
        self.max_requests = max_requests
        self.window_sec = window_sec
        self.requests = {}

    def is_rate_limited(self, user_id: str) -> bool:
        current_time = time.time()
        if user_id not in self.requests:
            self.requests[user_id] = []
        
        # Remove expired requests
        self.requests[user_id] = [req for req in self.requests[user_id] if current_time - req < self.window_sec]
        
        if len(self.requests[user_id]) >= self.max_requests:
            return True
        self.requests[user_id].append(current_time)
        return False

class FirestoreClient:
    def __init__(self) -> None:
        """Init the client."""
        credentials, _ = google.auth.default()
        self.client = firestore.Client(credentials=credentials)
        self.rate_limiter = RateLimiter(max_requests=5, window_sec=60)  # 5 requests per minute

    def get_parameters(self, user_id: str) -> dict:
        """Retrieve parameters with rate limiting."""
        if self.rate_limiter.is_rate_limited(user_id):
            raise Exception("Rate limit exceeded.")
        return self.get("parameters", "parameters")
